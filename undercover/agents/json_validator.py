





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
def extract_json_from_text(text):
    """
    Extract JSON object from text that might contain other content before or after the JSON.
    
    Args:
        text (str): Text that may contain a JSON object somewhere within it
        
    Returns:
        str: The extracted JSON string, or original string if no JSON object is found
    """
    import re
    
    # Look for text that starts with { and ends with } with balanced braces in between
    json_pattern = r'(\{(?:[^{}]|(?R))*\})'
    
    # Find all potential JSON objects in the text
    matches = re.findall(r'\{(?:[^{}]|\{(?:[^{}]|\{(?:[^{}])*\})*\})*\}', text)
    
    if not matches:
        return text  # No JSON-like structure found
    
    # Sort matches by length (descending) to prioritize the largest JSON object
    matches.sort(key=len, reverse=True)
    
    # Return the largest JSON-like structure found
    return matches[0]


def extract_json_improved(text):
    """
    A more robust approach to extract JSON from text with multiple fallback methods
    
    Args:
        text (str): Text that may contain a JSON object
        
    Returns:
        str: The extracted JSON string, or None if no valid JSON found
    """
    import json
    import re
    
    # First, try to find JSON using regex pattern matching
    # Find the first occurrence of a pattern that looks like a JSON object
    json_pattern = re.compile(r'(\{[^{]*\{.*\}[^}]*\}|\{[^{}]*\})')
    match = json_pattern.search(text)
    
    potential_jsons = []
    
    # If we found something that might be JSON, add it to candidates
    if match:
        potential_jsons.append(match.group(0))
    
    # Also try to extract anything between first { and last }
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
        potential_jsons.append(text[first_brace:last_brace+1])
    
    # Try all candidates
    for json_text in potential_jsons:
        try:
            # Check if it's valid JSON
            json.loads(json_text)
            return json_text
        except json.JSONDecodeError:
            continue
    
    # If nothing worked, try an even more aggressive approach:
    # Find all { and } and try combinations
    open_braces = [i for i, char in enumerate(text) if char == '{']
    close_braces = [i for i, char in enumerate(text) if char == '}']
    
    # Try different combinations of opening and closing braces
    for start in open_braces:
        for end in close_braces:
            if start < end:
                json_candidate = text[start:end+1]
                try:
                    json.loads(json_candidate)
                    return json_candidate
                except json.JSONDecodeError:
                    continue
    
    # If all else fails, return None
    return None


def safe_parse_json(json_str):
    """
    Safely parses a JSON string, attempting to fix common issues if there are errors.
    Now with improved extraction of JSON from text.
    
    Args:
        json_str (str): The string that may contain JSON (possibly with text before/after)
        
    Returns:
        tuple: (parsed_result_or_None, error_message_or_None)
    """
    import json
    
    # First, try to extract JSON from the text if there's non-JSON content
    json_str = extract_json_from_text(json_str)
    
    # Clean control characters that might cause issues
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
        
        # If the first extraction method failed, try the improved approach
        json_str = extract_json_improved(json_str)
        if json_str:
            try:
                result = json.loads(json_str)
                print("Improved JSON extraction successful!")
                return result, None
            except json.JSONDecodeError:
                pass  # Continue with other approaches
        
        return None, error_msg
    
    # Try to parse the JSON
    try:
        result = json.loads(cleaned_json)
        return result, None
    except json.JSONDecodeError as e:
        # If parsing still fails, try the improved extraction first
        print(f"Initial cleaning didn't work: {str(e)}")
        
        # Try the improved extraction method
        json_str = extract_json_improved(json_str)
        if json_str:
            try:
                result = json.loads(json_str)
                print("Improved JSON extraction successful after parsing error!")
                return result, None
            except json.JSONDecodeError:
                pass  # Continue with other approaches
        
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

# Import the extract_json functions from the previous artifact
def extract_json_from_text(text):
    """
    Extract JSON object from text that might contain other content before or after the JSON.
    
    Args:
        text (str): Text that may contain a JSON object somewhere within it
        
    Returns:
        str: The extracted JSON string, or original string if no JSON object is found
    """
    import re
    
    # Look for text that starts with { and ends with } with balanced braces in between
    # This pattern is simplified for readability
    matches = re.findall(r'\{(?:[^{}]|\{(?:[^{}]|\{(?:[^{}])*\})*\})*\}', text)
    
    if not matches:
        return text  # No JSON-like structure found
    
    # Sort matches by length (descending) to prioritize the largest JSON object
    matches.sort(key=len, reverse=True)
    
    # Return the largest JSON-like structure found
    return matches[0]

def extract_json_improved(text):
    """
    A more robust approach to extract JSON from text with multiple fallback methods
    
    Args:
        text (str): Text that may contain a JSON object
        
    Returns:
        str: The extracted JSON string, or None if no valid JSON found
    """
    import json
    import re
    
    # First, try to find JSON using regex pattern matching
    # Find the first occurrence of a pattern that looks like a JSON object
    json_pattern = re.compile(r'(\{[^{]*\{.*\}[^}]*\}|\{[^{}]*\})')
    match = json_pattern.search(text)
    
    potential_jsons = []
    
    # If we found something that might be JSON, add it to candidates
    if match:
        potential_jsons.append(match.group(0))
    
    # Also try to extract anything between first { and last }
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
        potential_jsons.append(text[first_brace:last_brace+1])
    
    # Try all candidates
    for json_text in potential_jsons:
        try:
            # Check if it's valid JSON
            json.loads(json_text)
            return json_text
        except json.JSONDecodeError:
            continue
    
    # If nothing worked, try an even more aggressive approach:
    # Find all { and } and try combinations
    open_braces = [i for i, char in enumerate(text) if char == '{']
    close_braces = [i for i, char in enumerate(text) if char == '}']
    
    # Try different combinations of opening and closing braces
    for start in open_braces:
        for end in close_braces:
            if start < end:
                json_candidate = text[start:end+1]
                try:
                    json.loads(json_candidate)
                    return json_candidate
                except json.JSONDecodeError:
                    continue
    
    # If all else fails, return None
    return None