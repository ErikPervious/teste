"""
Script para criar 30 repositorios privados no GitHub com 1 commit cada.
Usa a CLI 'gh' para criar os repos e git para os commits.

Uso:
  1. Certifique-se de ter o 'gh' instalado e autenticado (gh auth login)
  2. Execute: python generate_private_repos.py
"""

import os
import random
import subprocess
import sys
import tempfile
import shutil
from datetime import datetime, timedelta

# ─── CONFIGURACAO ────────────────────────────────────────────────────────────

GITHUB_USER = "ErikPervious"

# Periodo para datas aleatorias dos commits
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime.now()

# Nomes de projetos ficticios (30)
PROJECT_NAMES = [
    "api-gateway-service",
    "auth-microservice",
    "data-pipeline-etl",
    "dashboard-analytics",
    "notification-engine",
    "payment-processor",
    "user-management-api",
    "file-storage-service",
    "search-indexer",
    "cache-layer-proxy",
    "log-aggregator",
    "config-manager",
    "scheduler-service",
    "email-sender-worker",
    "report-generator",
    "webhook-dispatcher",
    "rate-limiter-module",
    "session-handler",
    "audit-trail-service",
    "feature-flag-system",
    "health-check-monitor",
    "token-validator",
    "image-resizer-lambda",
    "queue-consumer-worker",
    "backup-automation",
    "migration-toolkit",
    "api-docs-generator",
    "load-balancer-config",
    "secrets-manager-wrapper",
    "deploy-orchestrator",
]

# Mensagens iniciais possiveis
INIT_MESSAGES = [
    "chore: initial project setup",
    "feat: initial commit with base structure",
    "chore: bootstrap project",
    "feat: project scaffolding",
    "chore: initialize repository",
    "feat: add initial project files",
]

# Conteudo base para o README de cada projeto
README_TEMPLATES = [
    "# {name}\n\nInternal microservice for handling {desc}.\n\n## Setup\n\n```bash\nnpm install\nnpm start\n```\n",
    "# {name}\n\nBackend service for {desc}.\n\n## Requirements\n\n- Python 3.10+\n- Docker\n\n## Running\n\n```bash\npip install -r requirements.txt\npython main.py\n```\n",
    "# {name}\n\nPrivate module for {desc}.\n\n## Quick Start\n\n```bash\ndocker-compose up -d\n```\n",
    "# {name}\n\n{desc} service.\n\n## Development\n\n```bash\ngo build -o app .\n./app\n```\n",
]

DESCRIPTIONS = [
    "request routing and load distribution",
    "user authentication and authorization",
    "data extraction, transformation, and loading",
    "real-time metrics visualization",
    "push and email notifications",
    "payment processing and billing",
    "user CRUD operations",
    "file upload and storage management",
    "full-text search indexing",
    "caching and response optimization",
    "centralized log collection",
    "dynamic configuration management",
    "cron job scheduling",
    "transactional email delivery",
    "automated report generation",
    "webhook management and delivery",
    "API rate limiting",
    "session management",
    "audit logging and compliance",
    "feature flag management",
    "service health monitoring",
    "JWT token validation",
    "image processing and resizing",
    "message queue consumption",
    "automated backup routines",
    "database migration management",
    "API documentation generation",
    "load balancer configuration",
    "secrets and credentials management",
    "deployment orchestration",
]

# ─── FUNCOES ─────────────────────────────────────────────────────────────────


def run_cmd(cmd, cwd=None, env_extra=None):
    """Executa um comando e retorna o resultado."""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(
        cmd, cwd=cwd, env=env, capture_output=True, text=True, shell=True
    )
    return result


def random_date():
    """Gera uma data aleatoria entre START_DATE e END_DATE."""
    delta = (END_DATE - START_DATE).days
    rand_days = random.randint(0, delta)
    dt = START_DATE + timedelta(days=rand_days)
    hour = random.randint(8, 22)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return dt.replace(hour=hour, minute=minute, second=second)


def create_repo(name, description, index):
    """Cria um repo privado no GitHub com 1 commit."""
    print(f"\n[{index + 1}/30] Criando: {name}")

    # 1. Criar repo privado no GitHub via gh
    result = run_cmd(
        f'gh repo create {GITHUB_USER}/{name} --private --description "{description}" --confirm',
    )
    if result.returncode != 0:
        # Tentar formato alternativo do gh
        result = run_cmd(
            f'gh repo create {GITHUB_USER}/{name} --private -d "{description}" -y',
        )
    if result.returncode != 0:
        print(f"  ERRO ao criar repo: {result.stderr.strip()}")
        print(f"  Tentando sem --confirm...")
        result = run_cmd(
            f'gh repo create {GITHUB_USER}/{name} --private -d "{description}"',
        )
        if result.returncode != 0:
            print(f"  FALHOU: {result.stderr.strip()}")
            return False

    print(f"  Repo criado no GitHub")

    # 2. Criar diretorio temporario, fazer commit e push
    tmp_dir = os.path.join(tempfile.gettempdir(), f"repo_{name}")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)

    # Init
    run_cmd("git init", cwd=tmp_dir)

    # Criar README
    readme_template = random.choice(README_TEMPLATES)
    readme_content = readme_template.format(name=name, desc=description)
    with open(os.path.join(tmp_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Criar .gitignore basico
    with open(os.path.join(tmp_dir, ".gitignore"), "w", encoding="utf-8") as f:
        f.write("node_modules/\n.env\n__pycache__/\n*.pyc\n.vscode/\n.idea/\ndist/\nbuild/\n")

    # Commit com data aleatoria
    commit_date = random_date()
    date_str = commit_date.strftime("%Y-%m-%dT%H:%M:%S")
    message = random.choice(INIT_MESSAGES)

    run_cmd("git add -A", cwd=tmp_dir)

    env_dates = {
        "GIT_AUTHOR_DATE": date_str,
        "GIT_COMMITTER_DATE": date_str,
    }
    run_cmd(f'git commit -m "{message}"', cwd=tmp_dir, env_extra=env_dates)

    # Branch main
    run_cmd("git branch -M main", cwd=tmp_dir)

    # Remote + push
    remote_url = f"https://github.com/{GITHUB_USER}/{name}.git"
    run_cmd(f"git remote add origin {remote_url}", cwd=tmp_dir)
    result = run_cmd("git push -u origin main", cwd=tmp_dir)

    if result.returncode != 0:
        print(f"  ERRO no push: {result.stderr.strip()}")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return False

    print(f"  Commit: {date_str} - {message}")
    print(f"  Push OK!")

    # Limpar diretorio temporario
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return True


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  GERADOR DE REPOSITORIOS PRIVADOS")
    print("=" * 60)
    print(f"  Total de repos: {len(PROJECT_NAMES)}")
    print(f"  Usuario: {GITHUB_USER}")
    print(f"  Periodo dos commits: {START_DATE.strftime('%d/%m/%Y')} - {END_DATE.strftime('%d/%m/%Y')}")
    print()

    # Verificar se gh esta instalado e autenticado
    result = run_cmd("gh auth status")
    if result.returncode != 0:
        print("ERRO: 'gh' nao esta autenticado. Execute 'gh auth login' primeiro.")
        sys.exit(1)
    print("GitHub CLI autenticado.\n")

    confirm = input("Deseja criar os 30 repositorios privados? (s/n): ").strip().lower()
    if confirm != "s":
        print("Cancelado.")
        sys.exit(0)

    success = 0
    failed = 0

    for i, (name, desc) in enumerate(zip(PROJECT_NAMES, DESCRIPTIONS)):
        if create_repo(name, desc, i):
            success += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"  RESULTADO: {success} criados | {failed} falharam")
    print("=" * 60)


if __name__ == "__main__":
    main()
