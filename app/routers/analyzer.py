from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from app.schemas import WebpageCreate, RunStatus, InternalRunState
from app.database.auth import verify_token
from app.services import state_manager
from app.database.db_helpers import (
    upsert_webpage_record,
    create_run_record,
    update_run_status,
    update_webpage_status,
)
from app.services.analytics.browser_to_json_parser.browser_to_json_parser import parse_url
from app.services.analytics.json_parser.models import DocumentFactory
# from app.services.analytics.rules_analyzer.analyzer import
from app.services.report_generator import generate_report
import pprint
from pydantic import BaseModel, HttpUrl
from app.services.llm.predictor import predict_usability


router = APIRouter()

# ============================================================
#                PUBLIC ENDPOINT: START ANALYSIS
# ============================================================

from app.services.llm.predictor import predict_usability

@router.post("/webpages/analyze", response_model=dict)
async def analyze_webpage(payload: WebpageCreate):
    try:
        # 1. Парсим URL
        raw_json = await parse_url(str(payload.url))
        if raw_json is None:
            raise RuntimeError("Parser returned None (URL unreachable or invalid).")

        # 2. Преобразуем в DocumentModel
        document = DocumentFactory.load_from_json(raw_json)

        # 3. Выполняем WCAG-анализ
        analysis_result = run_wcag_analysis(document)

        # 4. Формируем полный отчёт анализа
        report = {
            "url": str(payload.url),
            **analysis_result
        }

        # ------------------------------
        # 5. LLM-Предсказание юзабилити
        # ------------------------------
        # передаём "сырые" данные документа в LLM
        try:
            usability_score = predict_usability(raw_json)
        except Exception as llm_error:
            # если что-то пошло не так в LLM — не ломаем анализ
            usability_score = None

        # 6. Добавляем в отчёт
        report["usability_score"] = usability_score

        # 7. Возвращаем результат
        return {
            "status": "completed",
            "report": report
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))





# ============================================================
#          BACKGROUND EXECUTION: NEW PARSER PIPELINE
# ============================================================

# ... (все импорты остались прежними)

from app.services.analytics.rules_analyzer.rules_factory import RulesFactory
from app.services.analytics.data_group.data_group import DataGroupExtractor
from app.services.analytics.rules_analyzer.analyzer import RuleViolation  # Замените на реальный путь
from typing import List, Dict, Any, cast



# ============================================================
#          PURE FUNCTION: WCAG ANALYSIS LOGIC
# ============================================================

def run_wcag_analysis(document) -> Dict[str, Any]:
    """
    Pure function that runs all WCAG rules on a DocumentModel
    and returns a structured report.
    """
    extractor = DataGroupExtractor()
    factory = RulesFactory(extractor)

    # Собираем все уникальные классы правил
    all_rule_classes = set()
    for rule_list in factory.RULES_MAP.values():
        all_rule_classes.update(rule_list)

    rule_instances = [RuleClass() for RuleClass in all_rule_classes]

    # Карта для поиска элементов по node_id
    element_map = {el.node_id: el for el in document.elements}

    passed_rules: List[Dict[str, Any]] = []
    failed_rules: List[Dict[str, Any]] = []

    for rule in rule_instances:
        try:
            violations: List[RuleViolation] = rule.check(document)
            rule_info = {
                "rule_id": getattr(rule, "id", rule.__class__.__name__),
                "description": getattr(rule, "description", "No description"),
            }

            if not violations:
                passed_rules.append(rule_info)
            else:
                enriched_violations = []
                for v in violations:
                    element = element_map.get(v.element_id)
                    enriched_violations.append({
                        "message": v.message,
                        "element_id": v.element_id,
                        "element_path": element.get_path() if element else "N/A",
                        "element_tag": element.tag if element else None,
                    })
                failed_rules.append({
                    **rule_info,
                    "violations_count": len(violations),
                    "violations": enriched_violations,
                })

        except Exception as e:
            # Обработка ошибок внутри правила
            failed_rules.append({
                "rule_id": getattr(rule, "id", rule.__class__.__name__),
                "description": getattr(rule, "description", "No description"),
                "violations_count": 1,
                "violations": [{
                    "message": f"Rule execution error: {str(e)}",
                    "element_id": "N/A",
                    "element_path": "N/A",
                    "element_tag": None,
                }]
            })

    return {
        "summary": {
            "total_rules": len(rule_instances),
            "passed_rules": len(passed_rules),
            "failed_rules": len(failed_rules),
            "total_violations": sum(fr["violations_count"] for fr in failed_rules),
        },
        "passed": passed_rules,
        "failed": failed_rules,
    }


# ============================================================
#          BACKGROUND EXECUTION: COORDINATOR
# ============================================================

async def analyze_webpage_background(
    run_id: str,
    webpage_id: str,
    url: str,
):
    try:
        await update_run_status(run_id, RunStatus.running)
        await update_webpage_status(webpage_id, RunStatus.running)
        await state_manager.set_running(UUID(run_id))

        # 1. Получить JSON-представление страницы
        raw_json = await parse_url(url)
        if raw_json is None:
            raise RuntimeError("Parser returned None (URL unreachable or invalid).")

        # 2. Преобразовать в DocumentModel
        document = DocumentFactory.load_from_json(raw_json)

        # 3. Выполнить анализ доступности
        analysis_result = run_wcag_analysis(document)

        # 4. Получить оценку юзабилити
        usability_score = predict_usability(raw_json)

        # 5. Сформировать полный отчёт
        report = {
            "url": url,
            "usability_score": f"{usability_score:.2f}",
            **analysis_result
        }

        # 6. (Опционально) сохранить в БД — раскомментируйте при реализации
        # await save_run_result(run_id, {"analysis_report": report})

        # Для отладки — выводим в консоль
        print("=== WCAG ANALYSIS REPORT ===")
        pprint.pprint(report)

        # 7. Завершить выполнение
        await update_run_status(run_id, RunStatus.completed)
        await update_webpage_status(webpage_id, RunStatus.completed)
        await state_manager.set_completed(UUID(run_id))

    except Exception as e:
        error_msg = str(e)
        await update_run_status(run_id, RunStatus.failed, error_msg)
        await update_webpage_status(webpage_id, RunStatus.failed)
        await state_manager.set_failed(UUID(run_id), error_msg)
        import traceback
        traceback.print_exc()


# ============================================================
#                    IN-MEMORY RUN STATE
# ============================================================

@router.get("/runs/{run_id}", response_model=InternalRunState)
async def get_run_state(run_id: UUID, user_id=Depends(verify_token)):
    state = await state_manager.get_run_state(run_id, user_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found or not yours")
    return state


@router.get("/webpages/{webpage_id}/runs", response_model=list[InternalRunState])
async def list_runs_for_webpage(webpage_id: UUID, user_id=Depends(verify_token)):
    return await state_manager.list_runs_for_webpage(webpage_id, user_id)
