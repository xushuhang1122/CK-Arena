# def validate_json_structure(json_str):
#     """
#     Validates the basic structure of a JSON string, checking for matching brackets and correct comma placement
    
#     Args:
#         json_str (str): The JSON string to validate
        
#     Returns:
#         tuple: (is_valid, error_message)
#     """
#     stack = []
#     in_string = False
#     escape_next = False
#     line_num = 1
#     col_num = 0
    
#     for i, char in enumerate(json_str):
#         col_num += 1
        
#         # Handle newlines, update line and column numbers
#         if char == '\n':
#             line_num += 1
#             col_num = 0
#             continue
            
#         # Handle characters within strings
#         if in_string:
#             if escape_next:
#                 escape_next = False
#             elif char == '\\':
#                 escape_next = True
#             elif char == '"':
#                 in_string = False
#             continue
        
#         # Handle characters outside strings
#         if char == '"':
#             in_string = True
#         elif char in '{[(':
#             stack.append((char, line_num, col_num))
#         elif char in '}])':
#             if not stack:
#                 return False, f"Error: Unmatched closing delimiter '{char}' at line {line_num}, column {col_num}"
            
#             last_open, open_line, open_col = stack.pop()
            
#             # Check if brackets match
#             if (char == '}' and last_open != '{') or \
#                (char == ']' and last_open != '[') or \
#                (char == ')' and last_open != '('):
#                 return False, f"Error: '{char}' at line {line_num}, column {col_num} doesn't match '{last_open}' at line {open_line}, column {open_col}"
        
#         # Check commas in objects and arrays
#         elif char == ',':
#             if stack and stack[-1][0] in '{[' and i+1 < len(json_str):
#                 # Find the next non-whitespace character
#                 next_char_idx = i + 1
#                 while next_char_idx < len(json_str) and json_str[next_char_idx].isspace():
#                     next_char_idx += 1
                
#                 if next_char_idx < len(json_str) and json_str[next_char_idx] in '}]':
#                     return False, f"Error: Trailing comma at line {line_num}, column {col_num} before the end of an object or array"
    
#     # Check for unclosed brackets
#     if stack:
#         last_open, open_line, open_col = stack[-1]
#         return False, f"Error: '{last_open}' at line {open_line}, column {open_col} has no matching closing delimiter"
    
#     return True, "JSON structure looks valid"

# def safe_parse_json(json_str):
#     """
#     Safely parses a JSON string, attempting to fix common issues if there are errors
    
#     Args:
#         json_str (str): The JSON string to parse
        
#     Returns:
#         tuple: (parsed_result_or_None, error_message_or_None)
#     """
#     import json
    
#     # First check the basic structure
#     is_valid, error_msg = validate_json_structure(json_str)
#     if not is_valid:
#         print(f"JSON validation failed: {error_msg}")
        
#         # Try to automatically fix missing closing braces
#         if "has no matching closing delimiter" in error_msg and "'{'" in error_msg:
#             fixed_json = json_str + "}"
#             print("Attempting to add missing closing brace...")
#             try:
#                 result = json.loads(fixed_json)
#                 print("Fix successful!")
#                 return result, None
#             except json.JSONDecodeError as e:
#                 return None, f"Fix attempt failed: {str(e)}"
        
#         return None, error_msg
    
#     # Try to parse the JSON
#     try:
#         result = json.loads(json_str)
#         return result, None
#     except json.JSONDecodeError as e:
#         return None, f"JSON parsing error: {str(e)}"







def validate_json_structure(json_str):
    """
    Validates the basic structure of a JSON string, checking for matching brackets and correct comma placement
    
    Args:
        json_str (str): The JSON string to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    stack = []
    in_string = False
    escape_next = False
    line_num = 1
    col_num = 0
    
    for i, char in enumerate(json_str):
        col_num += 1
        
        # Handle newlines, update line and column numbers
        if char == '\n':
            line_num += 1
            col_num = 0
            continue
            
        # Handle characters within strings
        if in_string:
            if escape_next:
                escape_next = False
            elif char == '\\':
                escape_next = True
            elif char == '"':
                in_string = False
            continue
        
        # Handle characters outside strings
        if char == '"':
            in_string = True
        elif char in '{[(':
            stack.append((char, line_num, col_num))
        elif char in '}])':
            if not stack:
                return False, f"Error: Unmatched closing delimiter '{char}' at line {line_num}, column {col_num}"
            
            last_open, open_line, open_col = stack.pop()
            
            # Check if brackets match
            if (char == '}' and last_open != '{') or \
               (char == ']' and last_open != '[') or \
               (char == ')' and last_open != '('):
                return False, f"Error: '{char}' at line {line_num}, column {col_num} doesn't match '{last_open}' at line {open_line}, column {open_col}"
        
        # Check commas in objects and arrays
        elif char == ',':
            if stack and stack[-1][0] in '{[' and i+1 < len(json_str):
                # Find the next non-whitespace character
                next_char_idx = i + 1
                while next_char_idx < len(json_str) and json_str[next_char_idx].isspace():
                    next_char_idx += 1
                
                if next_char_idx < len(json_str) and json_str[next_char_idx] in '}]':
                    return False, f"Error: Trailing comma at line {line_num}, column {col_num} before the end of an object or array"
    
    # Check for unclosed brackets
    if stack:
        last_open, open_line, open_col = stack[-1]
        return False, f"Error: '{last_open}' at line {open_line}, column {open_col} has no matching closing delimiter"
    
    return True, "JSON structure looks valid"

def clean_control_characters(json_str):
    """
    Cleans control characters in JSON strings that might cause parsing issues
    
    Args:
        json_str (str): The JSON string to clean
        
    Returns:
        str: The cleaned JSON string
    """
    import re
    
    # Function to clean each string value in the JSON
    def clean_string_content(match):
        # Match contains the quotes and string content
        string_content = match.group(0)
        # Only process if it's a proper string (starts and ends with ")
        if string_content.startswith('"') and string_content.endswith('"'):
            # Keep the surrounding quotes but clean the content inside
            inner_content = string_content[1:-1]
            # Replace problematic control characters with spaces or proper escapes
            cleaned = inner_content.replace('\n', ' ')  # Replace newlines with spaces
            cleaned = cleaned.replace('\r', ' ')        # Replace carriage returns with spaces
            cleaned = cleaned.replace('\t', ' ')        # Replace tabs with spaces
            # Handle other control characters if needed
            # Return with quotes restored
            return '"' + cleaned + '"'
        return string_content
    
    # This regex matches JSON string values including the quotes
    # It handles escaped quotes inside strings
    string_pattern = r'"(?:[^"\\]|\\["\\/bfnrt]|\\u[0-9a-fA-F]{4})*"'
    
    # Replace each string with its cleaned version
    cleaned_json = re.sub(string_pattern, clean_string_content, json_str)
    return cleaned_json

def safe_parse_json(json_str):
    """
    Safely parses a JSON string, attempting to fix common issues if there are errors
    
    Args:
        json_str (str): The JSON string to parse
        
    Returns:
        tuple: (parsed_result_or_None, error_message_or_None)
    """
    import json
    
    # First clean control characters that might cause issues
    cleaned_json = clean_control_characters(json_str)
    
    # Then check the basic structure
    is_valid, error_msg = validate_json_structure(cleaned_json)
    if not is_valid:
        print(f"JSON validation failed: {error_msg}")
        
        # Try to automatically fix missing closing braces
        if "has no matching closing delimiter" in error_msg and "'{'" in error_msg:
            fixed_json = cleaned_json + "}"
            print("Attempting to add missing closing brace...")
            try:
                result = json.loads(fixed_json)
                print("Fix successful!")
                return result, None
            except json.JSONDecodeError as e:
                return None, f"Fix attempt failed: {str(e)}"
        
        return None, error_msg
    
    # Try to parse the JSON
    try:
        result = json.loads(cleaned_json)
        return result, None
    except json.JSONDecodeError as e:
        # If parsing still fails, try a more aggressive approach
        print(f"Initial cleaning didn't work: {str(e)}")
        print("Trying more aggressive cleaning...")
        
        # More aggressive cleaning for specific cases
        if "Invalid control character" in str(e):
            # Replace all control characters (ASCII codes 0-31)
            aggressive_cleaned = ''
            for char in cleaned_json:
                if ord(char) >= 32 or char in '\n\r\t':
                    aggressive_cleaned += char
                else:
                    aggressive_cleaned += ' '  # Replace with space
            
            try:
                result = json.loads(aggressive_cleaned)
                print("Aggressive cleaning successful!")
                return result, None
            except json.JSONDecodeError as new_e:
                return None, f"Aggressive cleaning failed: {str(new_e)}"
        
        return None, f"JSON parsing error: {str(e)}"

