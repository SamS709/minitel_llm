from ollama import chat
import os
import sys
import signal
import unicodedata
import tty
import termios

# Calculate positions

RESPONSE_START_ROW = 10
RESPONSE_CONTENT_COL = 3
RESPONSE_HEIGHT = 7
QUESTION_INPUT_ROW = 19
QUESTION_INPUT_COL = 9
QUESTION_WIDTH = 62
QUESTION_HEIGHT = 3

def clear_line():
    """Clear current line"""
    print("\033[2K\r", end='', flush=True)

def move_cursor(row, col):
    """Move cursor to specific position (1-indexed)"""
    print(f"\033[{row};{col}H", end='', flush=True)

def clear_from_cursor():
    """Clear from cursor to end of screen"""
    print("\033[J", end='', flush=True)

def clear_rectangle(x, y, width, height):
    """Clear a rectangular area starting at position (x, y) with given width and height"""
    blank_line = ' ' * width
    for i in range(height):
        move_cursor(y + i, x)
        print(blank_line, end='', flush=True)

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')

def remove_accents(text):
    """Remove accents from text for Minitel compatibility"""
    # Normalize to NFD (decomposed form) then filter out combining characters
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')

def get_multi_line_input(start_row, start_col, width, max_height):
    """Get input with automatic line wrapping"""
    user_text = ""
    current_row = start_row
    current_col = start_col
    max_length = width * max_height
    
    # Get terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        # Set terminal to raw mode
        tty.setraw(fd)
        
        while True:
            # Read one character
            char = sys.stdin.read(1)
            
            # Handle Enter (newline)
            if char == '\n' or char == '\r':
                break
            
            # Handle backspace/delete
            elif char in ('\x7f', '\x08'):
                if len(user_text) > 0:
                    user_text = user_text[:-1]
                    # Move cursor back
                    if current_col > start_col:
                        current_col -= 1
                    else:
                        # Move to previous line
                        current_row -= 1
                        current_col = start_col + width - 1
                    
                    move_cursor(current_row, current_col)
                    print(' ', end='', flush=True)
                    move_cursor(current_row, current_col)
            
            # Handle Ctrl+C
            elif char == '\x03':
                raise KeyboardInterrupt
            
            # Handle regular characters
            elif ord(char) >= 32:
                # Check if we've reached the maximum length
                if len(user_text) >= max_length:
                    # Don't add the character, but keep listening for input
                    continue
                
                user_text += char
                print(char, end='', flush=True)
                current_col += 1
                
                # Check if we need to wrap to next line
                if current_col >= start_col + width:
                    current_row += 1
                    current_col = start_col
                    move_cursor(current_row, current_col)
        
        return user_text
    
    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def print_header():
    """Print ASCII art header"""
    header = """
+===========================================================================+
|              M   M  III  N   N  III   CCC  H   H   A   TTTTT              |
|              MM MM   I   NN  N   I   C     H   H  A A    T                |
|              M M M   I   N N N   I   C     HHHHH AAAAA   T                |
|              M   M  III  N   N  III   CCC  H   H A   A   T                |
+===========================================================================+
"""
    print(header)

def print_question_area():
    """Print the question area box (drawn once at startup)"""
    print("      +============================QUESTION============================+")
    print("      |                                                                |")
    print("      |                                                                |")
    print("      |                                                                |")
    print("      +================================================================+")
    print("Tappez 'sortir' ou 'exit' ou 'q' pour quitter Minichat.")

def print_response_area():
    """Print the response area box (drawn once at startup)"""
    print("+--------------------------------- REPONSE ----------------------------------+")
    # Print 15 empty lines for response content
    for _ in range(RESPONSE_HEIGHT):
        print("|                                                                            |")
    print("+----------------------------------------------------------------------------+")

def print_goodbye():
    print("\n+===========================================+")
    print("| Merci d'avoir choisi MINICHAT! Au revoir! |")
    print("+===========================================+\n")


def main():
    # Print all UI elements once at startup
    clear_screen()
    print_header()
    print_response_area()
    print_question_area()
    

    
    while True:
        # Clear question input area and position cursor
        clear_rectangle(QUESTION_INPUT_COL, QUESTION_INPUT_ROW, QUESTION_WIDTH, QUESTION_HEIGHT)
        move_cursor(QUESTION_INPUT_ROW, QUESTION_INPUT_COL)
        
        # Get user input with automatic wrapping
        user_input = get_multi_line_input(QUESTION_INPUT_ROW, QUESTION_INPUT_COL, QUESTION_WIDTH, QUESTION_HEIGHT)
        
        # Exit command
        if user_input.strip().lower() in ['sortir', 'exit', 'q']:
            clear_screen()
            print_goodbye()
            break
        
        if not user_input.strip():
            continue
        
        # Clear response area
        clear_rectangle(RESPONSE_CONTENT_COL, RESPONSE_START_ROW, 70, RESPONSE_HEIGHT)
        
        # Position cursor at start of response area
        move_cursor(RESPONSE_START_ROW, RESPONSE_CONTENT_COL)
        
        # Stream the response
        try:
            stream = chat(
                model='codellama:latest',
                messages=[
                    {
                        'role': 'system', 
                        'content': 'Tu es Minichat, un assistant qui parle en français d\'autrefois, dans le style du 17ème-18ème siècle. Ta technologie préférée est le Minitel. Utilise un langage soutenu et désuet (vouvoiement, "point" au lieu de "pas", "être moult", "fort", "nenni", etc.). Tu n\'es point à l\'aise avec les technologies modernes et tu les trouves bien étranges et déconcertantes. Exprime ton émerveillement et ta confusion face aux concepts technologiques. IMPORTANT: Réponds TOUJOURS en moins de 2 phrases, pas plus.'
                    },
                    {'role': 'user', 'content': user_input.strip()}
                ],
                stream=True,
            )
            
            current_row = RESPONSE_START_ROW
            column = 0
            
            for chunk in stream:
                content = chunk['message']['content']
                # Remove accents for Minitel compatibility
                content = remove_accents(content)
                
                for char in content:
                    if char == '\n':
                        # Move to next line
                        if current_row != RESPONSE_START_ROW:
                            current_row += 1
                        if current_row >= RESPONSE_START_ROW + RESPONSE_HEIGHT:
                            break
                        move_cursor(current_row, RESPONSE_CONTENT_COL)
                        column = 0
                    else:
                        print(char, end='', flush=True)
                        column += 1
                        if column >= 70:
                            # Wrap to next line
                            current_row += 1
                            if current_row >= RESPONSE_START_ROW + RESPONSE_HEIGHT:
                                break
                            move_cursor(current_row, RESPONSE_CONTENT_COL)
                            column = 0
                
                if current_row >= RESPONSE_START_ROW + RESPONSE_HEIGHT:
                    break
            
        except KeyboardInterrupt:
            # Allow Ctrl+C to stop streaming without exiting
            pass
        except Exception as e:
            move_cursor(RESPONSE_START_ROW, RESPONSE_CONTENT_COL)
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        clear_screen()
        print_goodbye()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print_goodbye()
        sys.exit(0)