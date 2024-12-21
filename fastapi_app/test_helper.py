import json
import sys

def parse_verification_code(json_str):
    try:
        data = json.loads(json_str)
        return data.get('code')
    except json.JSONDecodeError:
        return None

if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            json_str = f.read()
            code = parse_verification_code(json_str)
            if code:
                print(code)
