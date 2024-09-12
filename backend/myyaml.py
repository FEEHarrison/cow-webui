def parse_value(value):
    """
    解析 YAML 值。

    参数:
        value (str): 要解析的值。

    返回:
        解析后的值，可以是布尔值、整数、浮点数或字符串。
    """
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value.strip("'\"")

def simple_yaml_parse(file_content):
    def parse_value(value):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value.strip("'\"")

    result = {}
    current_section = result
    section_stack = []
    indent_stack = [0]

    for line in file_content.split('\n'):
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith('#'):
            continue

        indent = len(line) - len(line.lstrip())
        
        while indent < indent_stack[-1]:
            indent_stack.pop()
            current_section = section_stack.pop()

        if ':' in stripped_line:
            key, value = stripped_line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if value:
                current_section[key] = parse_value(value)
            else:
                new_section = {}
                current_section[key] = new_section
                section_stack.append(current_section)
                current_section = new_section
                indent_stack.append(indent)
        elif stripped_line.startswith('-'):
            value = stripped_line[1:].strip()
            if isinstance(current_section, list):
                current_section.append(parse_value(value))
            else:
                current_section = [parse_value(value)]
                section_stack[-1][list(section_stack[-1].keys())[-1]] = current_section

    # 处理嵌套的环境变量
    if 'services' in result and isinstance(result['services'], dict):
        for service in result['services'].values():
            if 'security_opt' in service and isinstance(service['security_opt'], dict):
                if 'environment' in service['security_opt']:
                    service['environment'] = service['security_opt']['environment']
                    del service['security_opt']['environment']
            if 'environment' in service:
                if isinstance(service['environment'], dict):
                    for key, value in service['environment'].items():
                        if isinstance(value, dict) and 'environment' in value:
                            service['environment'] = value['environment']
                            break
                elif isinstance(service['environment'], list):
                    env_dict = {}
                    for item in service['environment']:
                        if isinstance(item, str) and ':' in item:
                            key, value = item.split(':', 1)
                            env_dict[key.strip()] = value.strip()
                    service['environment'] = env_dict

    print(f"解析结果: {result}")
    return result
