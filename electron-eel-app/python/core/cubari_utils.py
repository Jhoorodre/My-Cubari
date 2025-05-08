import time
import json
import yaml

def generate_cubari_json(metadata, chapters_data):
    """
    Gera um JSON compatível com Cubari.moe
    
    metadata: dicionário com os metadados do mangá
    chapters_data: dicionário com dados dos capítulos
    """
    cubari_data = {
        "title": metadata.get("title", ""),
        "description": metadata.get("description", ""),
        "artist": metadata.get("artist", ""),
        "author": metadata.get("author", ""),
        "cover": metadata.get("cover", ""),
        "chapters": {}
    }
    
    for chapter_num, chapter_info in chapters_data.items():
        cubari_data["chapters"][str(chapter_num)] = {
            "title": chapter_info.get("title", str(chapter_num)),
            "volume": chapter_info.get("volume", ""),
            "last_updated": str(int(time.time())),
            "groups": {
                "": chapter_info.get("image_urls", [])
            }
        }
    
    return cubari_data

def generate_yaml(metadata, chapters_data):
    """
    Gera um YAML compatível com Cubari.moe
    
    metadata: dicionário com os metadados do mangá
    chapters_data: dicionário com dados dos capítulos
    """
    yaml_data = {
        "title": metadata.get("title", ""),
        "description": metadata.get("description", ""),
        "artist": metadata.get("artist", ""),
        "author": metadata.get("author", ""),
        "cover": metadata.get("cover", ""),
        "chapters": {}
    }
    
    for chapter_num, chapter_info in chapters_data.items():
        yaml_data["chapters"][str(chapter_num)] = {
            "title": chapter_info.get("title", str(chapter_num)),
            "volume": chapter_info.get("volume", ""),
            "groups": {
                "": chapter_info.get("album_url", "") # Em manga_uploader era album_url, em manga_processor era image_urls. Presumindo que para YAML, album_url é o desejado.
            }
        }
    
    return yaml_data

def save_json(data, output_file):
    """Salva dados em um arquivo JSON"""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return output_file

def save_yaml(data, output_file):
    """Salva dados em um arquivo YAML"""
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)
    return output_file
