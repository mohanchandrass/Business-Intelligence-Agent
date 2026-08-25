import asyncio
import sys
from app.infrastructure.monday.diagnostics import MondayDiagnostics
from app.infrastructure.llm.gemini import GeminiProvider
from app.config import get_settings

async def run_diagnostics():
    print("========================================")
    print("SKYLARK BI AGENT - CONNECTION DIAGNOSTICS")
    print("========================================\n")
    
    settings = get_settings()
    print("Configuration")
    print("[OK] Environment loaded\n")
    
    print("Monday.com")
    if settings.monday.api_token:
        print("[OK] Credentials present")
    else:
        print("[FAIL] Credentials missing")
        sys.exit(1)
        
    monday = MondayDiagnostics()
    
    auth_result = await monday.test_authentication()
    if auth_result["status"] == "success":
        print(f"[OK] Authentication (User: {auth_result['data'].get('name')})")
        print(f"[OK] API version ({settings.monday.api_version})")
    else:
        print(f"[FAIL] Authentication failed: {auth_result['message']}")
        
    deals_result = await monday.get_board_metadata(settings.monday.deals_board_id)
    if deals_result["status"] == "success":
        print(f"[OK] Deals board accessible ({deals_result['data'].get('name')})")
    else:
        print(f"[FAIL] Deals board failed: {deals_result['message']}")
        
    wo_result = await monday.get_board_metadata(settings.monday.work_orders_board_id)
    if wo_result["status"] == "success":
        print(f"[OK] Work Orders board accessible ({wo_result['data'].get('name')})")
    else:
        print(f"[FAIL] Work Orders board failed: {wo_result['message']}")
        
    print("\nGemini")
    if settings.gemini.api_key:
        print("[OK] Credentials present")
    else:
        print("[FAIL] Credentials missing")
        sys.exit(1)
        
    gemini = GeminiProvider()
    gemini_auth = await gemini.verify_authentication()
    if gemini_auth["status"] == "success":
        print(f"[OK] Model listing accessible ({gemini_auth['models_count']} models available)")
    else:
        print(f"[FAIL] Model listing failed: {gemini_auth['message']}")
        
    try:
        gen_result = await gemini.generate_text("Respond with the word OK.")
        if "OK" in gen_result.upper():
            print("[OK] Generation successful")
        else:
            print(f"[FAIL] Generation returned unexpected result: {gen_result}")
    except Exception as e:
        print(f"[FAIL] Generation failed: {str(e)}")

    print("\nNote: For data profiling, please run `python scripts/profile_data.py`")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
