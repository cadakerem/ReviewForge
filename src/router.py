def route_analysis(event_type: str, payload: dict) -> str:
    """
    Agentic Router Core:
    Gelen GitHub event'ini analiz ederek iÅŸlemin hafif analiz mi 
    yoksa derin analiz mi gerektirdiÄŸine karar verir.
    """
    if event_type == "push":
        commits = payload.get("commits", [])
        print(f"[Router] {len(commits)} commit inceleniyor...")
        
        # Kompleksite Ã¶lÃ§Ã¼mÃ¼ (Åimdilik basit bir kural tabanlÄ± yapÄ±)
        if len(commits) > 3:
            print("[Router] Karar: DEEP_ANALYSIS (Ã‡ok fazla commit var, Nemotron/GPT-OSS kullanÄ±lacak)")
            return "DEEP_ANALYSIS"
        
        print("[Router] Karar: LIGHT_ANALYSIS (Ufak deÄŸiÅŸiklik, Llama/Gemma kullanÄ±lacak)")
        return "LIGHT_ANALYSIS"
        
    elif event_type == "pull_request":
        action = payload.get("action")
        pr_data = payload.get("pull_request", {})
        pr_title = pr_data.get("title", "").lower()
        
        print(f"[Router] PR: '{pr_title}' | Aksiyon: {action}")
        
        # Sadece aÃ§Ä±k veya gÃ¼ncellenmiÅŸ PR'larÄ± analiz et
        if action not in ["opened", "synchronize", "reopened"]:
            return "IGNORED_ACTION"
            
        # Kritik baÅŸlÄ±klar gÃ¼venlik/mimari analizi gerektirir
        critical_keywords = ["sec", "auth", "architecture", "refactor", "core"]
        if any(keyword in pr_title for keyword in critical_keywords):
            print("[Router] Karar: DEEP_ANALYSIS (Kritik baÅŸlÄ±k tespit edildi)")
            return "DEEP_ANALYSIS"
            
        print("[Router] Karar: LIGHT_ANALYSIS (Standart PR)")
        return "LIGHT_ANALYSIS"
    
    return "UNKNOWN_EVENT"
