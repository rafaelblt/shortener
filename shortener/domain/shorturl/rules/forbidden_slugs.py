FORBIDDEN_SLUGS = {
    "docs",
    "admin", 
    "login", 
    "logout", 
    "dashboard", 
    "api", 
    "config", 
    "help", 
    "support", 
    "terms", 
    "privacy", 
    "about", 
    "contact"
}

def is_slug_forbidden(slug: str) -> bool:
    return slug.lower() in FORBIDDEN_SLUGS
