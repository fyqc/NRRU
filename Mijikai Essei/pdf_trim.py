'''
When copy text from .pdf to Microsoft Word, the format is not very desirable due to the line break.
This code is used to trim the contents.
It has four different codes, the current third one works best so far.

To use, create a '787.txt' file.
copy the text from any pdf, pasted in to 787.txt, save it, run this script, and the formatted text will be available inside '787.txt'.
Then you can select all from 787.txt, and paste into your Word notes.
'''

# def format_pdf_text(input_file, output_file):
#     """
#     Read a text file with PDF content and format it according to requirements:
#     - Remove "Teaching Points" line
#     - Fix line breaks for better readability
#     - Ensure proper formatting of lists
    
#     Args:
#         input_file (str): Path to the input text file
#         output_file (str): Path to the output text file
#     """
#     with open(input_file, 'r', encoding='utf-8') as f:
#         content = f.read()
    
#     # Split content into lines
#     lines = content.split('\n')
    
#     # Remove "Teaching Points" line
#     lines = [line for line in lines if line.strip() != "Teaching Points"]
#     lines = [line for line in lines if line.strip() != "Student Notes"]
    
#     # Process lines to fix formatting
#     formatted_lines = []
#     buffer = ""
    
#     i = 0
#     while i < len(lines):
#         line = lines[i].strip()
        
#         # Skip empty lines
#         if not line:
#             i += 1
#             continue
        
#         # Check if this is a numbered line
#         if line and (line[0].isdigit() and '. ' in line[:5]):
#             # If we have content in buffer, add it to formatted lines
#             if buffer:
#                 formatted_lines.append(buffer)
#                 buffer = ""
            
#             # Start collecting the numbered item
#             buffer = line
            
#             # Look ahead to see if next line is a continuation
#             j = i + 1
#             while j < len(lines) and lines[j].strip() and not (lines[j].strip()[0].isdigit() and '. ' in lines[j].strip()[:5]) and not lines[j].strip().startswith('-'):
#                 buffer += " " + lines[j].strip()
#                 j += 1
            
#             # Add the completed numbered item
#             formatted_lines.append(buffer)
#             buffer = ""
#             i = j
            
#         # Check if this is a bullet point
#         elif line.startswith('-'):
#             # If we have content in buffer, add it to formatted lines
#             if buffer:
#                 formatted_lines.append(buffer)
#                 buffer = ""
            
#             # Start collecting the bullet point
#             buffer = line
            
#             # Look ahead to see if next line is a continuation
#             j = i + 1
#             while j < len(lines) and lines[j].strip() and not (lines[j].strip()[0].isdigit() and '. ' in lines[j].strip()[:5]) and not lines[j].strip().startswith('-'):
#                 buffer += " " + lines[j].strip()
#                 j += 1
            
#             # Add the completed bullet point
#             formatted_lines.append(buffer)
#             buffer = ""
#             i = j
            
#         # Regular line
#         else:
#             if buffer:
#                 buffer += " " + line
#             else:
#                 buffer = line
#             i += 1
    
#     # Add any remaining buffer content
#     if buffer:
#         formatted_lines.append(buffer)
    
#     # Write the formatted content to output file
#     with open(output_file, 'w', encoding='utf-8') as f:
#         f.write('\n'.join(formatted_lines))
    
#     print(f"Formatted content saved to {output_file}")

# # Example usage

# if __name__ == '__main__':
#     input_file = "787.txt"
#     output_file = "787.txt"
#     format_pdf_text(input_file, output_file)

'''
v2
'''
# def format_pdf_text(input_file, output_file):
#     """
#     Read a text file with PDF content and format it according to requirements:
#     - Remove "Teaching Points" line
#     - Fix line breaks for better readability
#     - Ensure proper formatting of lists
#     - Preserve empty lines and line breaks after periods
    
#     Args:
#         input_file (str): Path to the input text file
#         output_file (str): Path to the output text file
#     """
#     with open(input_file, 'r', encoding='utf-8') as f:
#         content = f.read()
    
#     # Process the content in paragraphs to preserve empty lines
#     paragraphs = content.split('\n\n')
#     formatted_paragraphs = []
    
#     for paragraph in paragraphs:
#         lines = paragraph.split('\n')
        
#         # Skip "Teaching Points" paragraph
#         if len(lines) == 1 and lines[0].strip() == "Teaching Points":
#             continue
#         if len(lines) == 1 and lines[0].strip() == "Student Notes":
#             continue
        
#         # Process each paragraph
#         processed_lines = []
#         i = 0
#         while i < len(lines):
#             line = lines[i].strip()
            
#             # Skip empty lines within paragraphs but remember them
#             if not line:
#                 processed_lines.append('')
#                 i += 1
#                 continue
            
#             # Check if this is a numbered line or headline
#             if (line[0].isdigit() and '. ' in line[:5]) or (i == 0 and "Description" in line):
#                 current_line = line
                
#                 # Look ahead to see if next line is a continuation (not a bullet, not a number)
#                 j = i + 1
#                 while j < len(lines) and lines[j].strip() and not (lines[j].strip()[0].isdigit() and '. ' in lines[j].strip()[:5]) and not lines[j].strip().startswith('-'):
#                     # If the previous line ends with a period, preserve the line break
#                     if current_line.endswith('.'):
#                         processed_lines.append(current_line)
#                         current_line = lines[j].strip()
#                     else:
#                         current_line += " " + lines[j].strip()
#                     j += 1
                
#                 processed_lines.append(current_line)
#                 i = j
                
#             # Check if this is a bullet point
#             elif line.startswith('-'):
#                 current_line = line
                
#                 # Look ahead to see if next line is a continuation
#                 j = i + 1
#                 while j < len(lines) and lines[j].strip() and not (lines[j].strip()[0].isdigit() and '. ' in lines[j].strip()[:5]) and not lines[j].strip().startswith('-'):
#                     # If the previous line ends with a period, preserve the line break
#                     if current_line.endswith('.'):
#                         processed_lines.append(current_line)
#                         current_line = lines[j].strip()
#                     else:
#                         current_line += " " + lines[j].strip()
#                     j += 1
                
#                 processed_lines.append(current_line)
#                 i = j
                
#             # Regular line
#             else:
#                 processed_lines.append(line)
#                 i += 1
        
#         # Add the processed paragraph
#         if processed_lines:
#             formatted_paragraphs.append('\n'.join(processed_lines))
    
#     # Join paragraphs with double newlines to preserve paragraph separation
#     formatted_content = '\n\n'.join(formatted_paragraphs)
    
#     # Write the formatted content to output file
#     with open(output_file, 'w', encoding='utf-8') as f:
#         f.write(formatted_content)
    
#     print(f"Formatted content saved to {output_file}")

# Example usage
# if __name__ == "__main__":
#     input_file = "787.txt"
#     output_file = "787.txt"
#     format_pdf_text(input_file, output_file)

'''
v3
'''

def format_pdf_text(input_file, output_file):
    """
    Read a text file with PDF content and format it according to requirements:
    - Remove "Teaching Points" line
    - Fix line breaks for better readability
    - Ensure proper formatting of lists
    - Preserve empty lines and paragraph structure
    
    Args:
        input_file (str): Path to the input text file
        output_file (str): Path to the output text file
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Remove "Teaching Points" line
    filtered_lines = []
    skip_next = False
    for i, line in enumerate(lines):
        # Skip the line that contains "Teaching Points"
        if "Teaching Points" in line.strip():
            skip_next = False
            continue

        if "Student Notes" in line.strip():
            skip_next = False
            continue
        
        # Add the line to our filtered list
        filtered_lines.append(line)
    
    # Process the filtered lines to fix formatting
    formatted_lines = []
    i = 0
    while i < len(filtered_lines):
        current_line = filtered_lines[i].strip()
        
        # Skip empty lines but preserve them
        if not current_line:
            formatted_lines.append("")
            i += 1
            continue
        
        # Check if this is a heading (not numbered and not a bullet point)
        if (not current_line[0].isdigit() or '. ' not in current_line[:5]) and not current_line.startswith('-'):
            # Look ahead to see if next lines are continuation of this heading/paragraph
            paragraph_lines = [current_line]
            j = i + 1
            
            # Keep collecting lines until we hit a numbered item, bullet point, or empty line
            while j < len(filtered_lines):
                next_line = filtered_lines[j].strip()
                
                # Stop if we hit an empty line
                if not next_line:
                    break
                
                # Stop if we hit a numbered item
                if next_line[0].isdigit() and '. ' in next_line[:5]:
                    break
                
                # Stop if we hit a bullet point
                if next_line.startswith('-'):
                    break
                
                # Otherwise, this is part of the current paragraph
                paragraph_lines.append(next_line)
                j += 1
            
            # If we have multiple lines, process them as a paragraph
            if len(paragraph_lines) > 1:
                # Keep the first line as is
                formatted_lines.append(paragraph_lines[0])
                
                # For subsequent lines, check if the previous line ends with a period
                for k in range(1, len(paragraph_lines)):
                    prev_line = paragraph_lines[k-1]
                    if prev_line.endswith('.'):
                        # If the previous line ends with a period, keep the line break
                        formatted_lines.append(paragraph_lines[k])
                    else:
                        # Otherwise, merge with the previous line
                        formatted_lines[-1] += " " + paragraph_lines[k]
            else:
                # Single line paragraph
                formatted_lines.append(paragraph_lines[0])
            
            i = j
        
        # Check if this is a numbered item
        elif current_line[0].isdigit() and '. ' in current_line[:5]:
            # Add the numbered item
            formatted_lines.append(current_line)
            
            # Look for potential bullet points or continuations
            j = i + 1
            while j < len(filtered_lines):
                next_line = filtered_lines[j].strip()
                
                # Stop if we hit an empty line
                if not next_line:
                    break
                
                # Stop if we hit another numbered item
                if next_line[0].isdigit() and '. ' in next_line[:5]:
                    break
                
                # If this is a bullet point, add it as is
                if next_line.startswith('-'):
                    formatted_lines.append(next_line)
                    j += 1
                    continue
                
                # Otherwise, this is a continuation of the previous line
                # Check if the previous line ends with a period
                prev_line = formatted_lines[-1]
                if prev_line.endswith('.'):
                    # Keep the line break
                    formatted_lines.append(next_line)
                else:
                    # Merge with the previous line
                    formatted_lines[-1] += " " + next_line
                
                j += 1
            
            i = j
        
        # Check if this is a bullet point
        elif current_line.startswith('-'):
            # Add the bullet point
            formatted_lines.append(current_line)
            
            # Look for potential continuations
            j = i + 1
            while j < len(filtered_lines):
                next_line = filtered_lines[j].strip()
                
                # Stop if we hit an empty line
                if not next_line:
                    break
                
                # Stop if we hit a numbered item
                if next_line[0].isdigit() and '. ' in next_line[:5]:
                    break
                
                # Stop if we hit another bullet point
                if next_line.startswith('-'):
                    break
                
                # Otherwise, this is a continuation of the bullet point
                # Check if the previous line ends with a period
                prev_line = formatted_lines[-1]
                if prev_line.endswith('.'):
                    # Keep the line break
                    formatted_lines.append(next_line)
                else:
                    # Merge with the previous line
                    formatted_lines[-1] += " " + next_line
                
                j += 1
            
            i = j
        
        # Any other line
        else:
            formatted_lines.append(current_line)
            i += 1
    
    # Write the formatted content to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(formatted_lines))
    
    print(f"Formatted content saved to {output_file}")

# Example usage
if __name__ == "__main__":
    input_file = "787.txt"
    output_file = "787.txt"
    format_pdf_text(input_file, output_file)

'''
v4 Grok
'''

# def format_pdf_text(input_file, output_file):
#     """
#     Read a text file with PDF content and format it according to requirements:
#     - Remove "Teaching Points" line
#     - Fix line breaks for better readability
#     - Ensure proper formatting of lists
#     - Preserve empty lines and paragraph structure
#     - Preserve specific headings on separate lines
    
#     Args:
#         input_file (str): Path to the input text file
#         output_file (str): Path to the output text file
#     """
#     with open(input_file, 'r', encoding='utf-8') as f:
#         lines = f.readlines()
    
#     # Remove "Teaching Points" line
#     filtered_lines = []
#     skip_next = False
#     for i, line in enumerate(lines):
#         # Skip the line that contains "Teaching Points"
#         if "Teaching Points" in line.strip():
#             skip_next = False
#             continue

#         if "Student Notes" in line.strip():
#             skip_next = False
#             continue
        
#         # Add the line to our filtered list
#         filtered_lines.append(line)
    
#     # Process the filtered lines to fix formatting
#     formatted_lines = []
#     i = 0
#     while i < len(filtered_lines):
#         current_line = filtered_lines[i].strip()
        
#         # Skip empty lines but preserve them
#         if not current_line:
#             formatted_lines.append("")
#             i += 1
#             continue
        
#         # Check if this is a heading (not numbered and not a bullet point)
#         if (not current_line[0].isdigit() or '. ' not in current_line[:5]) and not current_line.startswith('-'):
#             # Look ahead to see if next lines are continuation of this heading/paragraph
#             paragraph_lines = [current_line]
#             j = i + 1
            
#             # Keep collecting lines until we hit a numbered item, bullet point, or empty line
#             while j < len(filtered_lines):
#                 next_line = filtered_lines[j].strip()
                
#                 # Stop if we hit an empty line
#                 if not next_line:
#                     break
                
#                 # Stop if we hit a numbered item
#                 if next_line[0].isdigit() and '. ' in next_line[:5]:
#                     break
                
#                 # Stop if we hit a bullet point
#                 if next_line.startswith('-'):
#                     break
                
#                 # Otherwise, this is part of the current paragraph
#                 paragraph_lines.append(next_line)
#                 j += 1
            
#             # If we have multiple lines, process them as a paragraph
#             if len(paragraph_lines) > 1:
#                 # Check if the lines are likely headings (e.g., short length or specific keywords)
#                 for k, line in enumerate(paragraph_lines):
#                     # Preserve line breaks for short lines or specific headings
#                     if (len(line) < 50 or  # Adjust threshold as needed
#                         any(keyword in line for keyword in ["System Description Section (SDS)", "Purpose"])):
#                         formatted_lines.append(line)
#                     else:
#                         # For non-heading lines, apply existing merging logic
#                         if formatted_lines and not formatted_lines[-1].endswith('.'):
#                             formatted_lines[-1] += " " + line
#                         else:
#                             formatted_lines.append(line)
#             else:
#                 # Single line paragraph
#                 formatted_lines.append(paragraph_lines[0])
            
#             i = j
        
#         # Check if this is a numbered item
#         elif current_line[0].isdigit() and '. ' in current_line[:5]:
#             # Add the numbered item
#             formatted_lines.append(current_line)
            
#             # Look for potential bullet points or continuations
#             j = i + 1
#             while j < len(filtered_lines):
#                 next_line = filtered_lines[j].strip()
                
#                 # Stop if we hit an empty line
#                 if not next_line:
#                     break
                
#                 # Stop if we hit another numbered item
#                 if next_line[0].isdigit() and '. ' in next_line[:5]:
#                     break
                
#                 # If this is a bullet point, add it as is
#                 if next_line.startswith('-'):
#                     formatted_lines.append(next_line)
#                     j += 1
#                     continue
                
#                 # Otherwise, this is a continuation of the previous line
#                 # Check if the previous line ends with a period
#                 prev_line = formatted_lines[-1]
#                 if prev_line.endswith('.'):
#                     # Keep the line break
#                     formatted_lines.append(next_line)
#                 else:
#                     # Merge with the previous line
#                     formatted_lines[-1] += " " + next_line
                
#                 j += 1
            
#             i = j
        
#         # Check if this is a bullet point
#         elif current_line.startswith('-'):
#             # Add the bullet point
#             formatted_lines.append(current_line)
            
#             # Look for potential continuations
#             j = i + 1
#             while j < len(filtered_lines):
#                 next_line = filtered_lines[j].strip()
                
#                 # Stop if we hit an empty line
#                 if not next_line:
#                     break
                
#                 # Stop if we hit a numbered item
#                 if next_line[0].isdigit() and '. ' in next_line[:5]:
#                     break
                
#                 # Stop if we hit another bullet point
#                 if next_line.startswith('-'):
#                     break
                
#                 # Otherwise, this is a continuation of the bullet point
#                 # Check if the previous line ends with a period
#                 prev_line = formatted_lines[-1]
#                 if prev_line.endswith('.'):
#                     # Keep the line break
#                     formatted_lines.append(next_line)
#                 else:
#                     # Merge with the previous line
#                     formatted_lines[-1] += " " + next_line
                
#                 j += 1
            
#             i = j
        
#         # Any other line
#         else:
#             formatted_lines.append(current_line)
#             i += 1
    
#     # Write the formatted content to output file
#     with open(output_file, 'w', encoding='utf-8') as f:
#         f.write('\n'.join(formatted_lines))
    
#     print(f"Formatted content saved to {output_file}")

# # Example usage
# if __name__ == "__main__":
#     input_file = "787.txt"
#     output_file = "787.txt"
#     format_pdf_text(input_file, output_file)
