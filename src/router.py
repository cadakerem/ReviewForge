def route_analysis(event_type: str, payload: dict) -> str:
    """
    Agentic Router Core:
    Gelen GitHub event'ini analiz ederek işlemin hafif analiz mi 
    yoksa derin analiz mi gerektirdiğine karar verir.
    """
    if event_type == "push":
        commits = payload.get("commits", [])
        print(f"[Router] {len(commits)} commit inceleniyor...")
        
        # Kompleksite ölçümü (Şimdilik basit bir kural tabanlı yapı)
        if len(commits) > 3:
            print("[Router] Karar: DEEP_ANALYSIS (Çok fazla commit var, Nemotron/GPT-OSS kullanılacak)")
            return "DEEP_ANALYSIS"
        
        print("[Router] Karar: LIGHT_ANALYSIS (Ufak değişiklik, Llama/Gemma kullanılacak)")
        return "LIGHT_ANALYSIS"
        
    elif event_type == "pull_request":
        action = payload.get("action")
        pr_data = payload.get("pull_request", {})
        pr_title = pr_data.get("title", "").lower()
        
        print(f"[Router] PR: '{pr_title}' | Aksiyon: {action}")
        
        # Sadece açık veya güncellenmiş PR'ları analiz et
        if action not in ["opened", "synchronize", "reopened"]:
            return "IGNORED_ACTION"
            
        # Kritik başlıklar güvenlik/mimari analizi gerektirir
        critical_keywords = ["sec", "auth", "architecture", "refactor", "core"]
        if any(keyword in pr_title for keyword in critical_keywords):
            print("[Router] Karar: DEEP_ANALYSIS (Kritik başlık tespit edildi)")
            return "DEEP_ANALYSIS"
            
        print("[Router] Karar: LIGHT_ANALYSIS (Standart PR)")
        return "LIGHT_ANALYSIS"
    
    return "UNKNOWN_EVENT"
