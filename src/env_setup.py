import os
import shutil

TEMPLATE_FILE = ".env.template"
ENV_FILE = "setting.env"

def ensure_env_file():
    if not os.path.exists(ENV_FILE):
        if os.path.exists(TEMPLATE_FILE):
            shutil.copyfile(TEMPLATE_FILE, ENV_FILE)
            print(f"✅ '{ENV_FILE}' を '{TEMPLATE_FILE}' から作成しました。")
        else:
            print(f"⚠️ '{TEMPLATE_FILE}' が存在しないため、'{ENV_FILE}' を作成できません。")
    else:
        print(f"✅ '{ENV_FILE}' は既に存在します。")

if __name__ == "__main__":
    ensure_env_file()