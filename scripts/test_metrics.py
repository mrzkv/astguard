import os
import sys
import subprocess
import json
from pathlib import Path

# Добавляем путь к проекту в начало sys.path для импорта локального astguard
sys.path.insert(0, os.getcwd())

from astguard.analyzer import StaticAnalyzer
from astguard.vulnerabilities import DANGEROUS_FUNCTIONS

def generate_safe_code(cwe_id):
    """Генерирует список безопасных примеров кода для данного CWE."""
    samples = {
        "CWE-94": [
            "eval('1+1')",
            "exec('pass')",
            "import ast\nast.literal_eval('[1, 2, 3]')",
            "compile('a=1', '', 'exec')",
            "eval('abs(-1)')"
        ],
        "CWE-78": [
            "import subprocess\nsubprocess.run(['ls'], shell=False)",
            "os.system('ls')",
            "subprocess.call(['ping', '127.0.0.1'])",
            "subprocess.check_call(['true'])",
            "subprocess.Popen(['echo', 'hi'])"
        ],
        "CWE-502": [
            "import json\njson.loads('{\"a\": 1}')",
            "import json\njson.load(open('config.json'))",
            "import yaml\nyaml.safe_load('a: 1')",
            "import pickle\npickle.dumps({'a': 1})",
            "# Safe data usage\npass"
        ],
        "CWE-22": [
            "with open('safe.txt', 'r') as f: f.read()",
            "os.path.join('/home/user', 'documents')",
            "import os\nos.path.exists('file.txt')",
            "open('/dev/null', 'w')",
            "from pathlib import Path\nPath('local.txt').open()"
        ],
        "CWE-327": [
            "import hashlib\nhashlib.sha256(b'data')",
            "hashlib.sha512(b'data')",
            "import hashlib\nhashlib.new('sha256')",
            "import hmac\nhmac.new(b'key', b'msg', digestmod='sha256')",
            "import secrets\nsecrets.compare_digest('a', 'b')"
        ],
        "CWE-798": [
            "password = os.getenv('DB_PASSWORD')",
            "api_key = ''",
            "token = None",
            "secret = 'REDACTED'",
            "credentials = {'user': 'admin'}"
        ],
        "CWE-489": [
            "app.run(debug=False)",
            "DEBUG = False\napp.run(debug=DEBUG)",
            "app.config['DEBUG'] = False",
            "if False: print('debug')",
            "import logging\nlogging.debug('message')"
        ],
        "CWE-89": [
            "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
            "cursor.execute('SELECT * FROM users')",
            "db.execute('INSERT INTO logs VALUES (1)')",
            "query = 'SELECT 1'\ncursor.execute(query)",
            "params = (1,)\ncursor.execute('SELECT * FROM t WHERE id=?', params)"
        ],
        "CWE-611": [
            "import xml.etree.ElementTree as ET\nET.parse('safe.xml')",
            "from lxml import etree\nparser = etree.XMLParser(resolve_entities=False)",
            "import xml.etree.ElementTree as ET\nET.fromstring('<root/>')",
            "import xml.etree.ElementTree as ET\ntree = ET.ElementTree(ET.Element('root'))",
            "import xml.etree.ElementTree as ET\nxml_data = ET.tostring(ET.Element('root'))"
        ],
    }
    return samples.get(cwe_id, ["pass"])

def run_benchmark():
    analyzer = StaticAnalyzer()
    
    # CWE_ID -> {TP, FP, TN, FN}
    metrics = {cwe_id: {"TP": 0, "FP": 0, "TN": 0, "FN": 0} for cwe_id in DANGEROUS_FUNCTIONS}
    
    # 1. Тестируем TP и FN на существующих уязвимых вариантах
    variants_dir = Path("tests/generated_variants")
    if variants_dir.exists():
        for cwe_dir in variants_dir.iterdir():
            if not cwe_dir.is_dir(): continue
            cwe_id = cwe_dir.name
            if cwe_id not in metrics: continue
            
            for test_file in cwe_dir.glob("*.py"):
                # Создаем новый анализатор для каждого файла, чтобы избежать сохранения состояния
                file_analyzer = StaticAnalyzer()
                findings = file_analyzer.run_analysis(test_file)
                found_cwe = any(f.cwe_details and f.cwe_details.cwe_id == cwe_id for f in findings)
                
                if found_cwe:
                    metrics[cwe_id]["TP"] += 1
                else:
                    metrics[cwe_id]["FN"] += 1
                    
    # 2. Тестируем TN и FP на безопасном коде
    safe_dir = Path("tests/temp_safe_variants")
    safe_dir.mkdir(exist_ok=True)
    
    for cwe_id in DANGEROUS_FUNCTIONS:
        codes = generate_safe_code(cwe_id)
        for i, code in enumerate(codes):
            safe_file = safe_dir / f"safe_{cwe_id}_{i}.py"
            with open(safe_file, "w") as f:
                f.write(code)
                
            file_analyzer = StaticAnalyzer()
            findings = file_analyzer.run_analysis(safe_file)
            found_cwe = any(f.cwe_details and f.cwe_details.cwe_id == cwe_id for f in findings)
            
            if found_cwe:
                metrics[cwe_id]["FP"] += 1
            else:
                metrics[cwe_id]["TN"] += 1
            
    # Удаляем временную папку
    import shutil
    shutil.rmtree(safe_dir)
    
    # Печать Markdown таблицы
    print("| Класс уязвимости (CWE) | Кол-во тестов | TP | FP | TN | FN | Precision | Recall |")
    print("|------------------------|---------------|----|----|----|----|-----------|--------|")
    
    total_tp = total_fp = total_tn = total_fn = 0
    
    for cwe_id in sorted(metrics.keys()):
        m = metrics[cwe_id]
        tp, fp, tn, fn = m["TP"], m["FP"], m["TN"], m["FN"]
        total_tests = tp + fp + tn + fn
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        
        print(f"| {cwe_id:<22} | {total_tests:<13} | {tp:<2} | {fp:<2} | {tn:<2} | {fn:<2} | {precision:<9.2f} | {recall:<6.2f} |")
        
        total_tp += tp
        total_fp += fp
        total_tn += tn
        total_fn += fn

    total_tests = total_tp + total_fp + total_tn + total_fn
    total_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    total_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
    
    print(f"| {'**TOTAL**':<22} | {total_tests:<13} | {total_tp:<2} | {total_fp:<2} | {total_tn:<2} | {total_fn:<2} | {total_precision:<9.2f} | {total_recall:<6.2f} |")

if __name__ == "__main__":
    run_benchmark()
