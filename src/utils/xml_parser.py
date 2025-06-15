# utils/xml_parser.py
from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PySide6.QtWidgets import QTextEdit
from lxml import etree as ET
import re


class XMLParserSignals(QObject):
    """Signals class for XMLParserThread operations."""
    finished = Signal(dict)
    error_occurred = Signal(str, str)
    program_output_progress = Signal(str)
    validation_result = Signal(bool, str)
    transformation_complete = Signal(str)


class XMLUtils:
    """Utility class for XML operations that don't require threading."""
    
    @staticmethod
    def validate_xml_syntax(xml_content: str) -> tuple[bool, str]:
        """Validate XML syntax without parsing the full document.
        
        Args:
            xml_content: XML content as string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            ET.fromstring(xml_content)
            return True, "XML syntax is valid"
        except ET.XMLSyntaxError as e:
            return False, f"XML syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def get_xml_encoding(file_path: str) -> str:
        """Extract encoding from XML file declaration.
        
        Args:
            file_path: Path to XML file
            
        Returns:
            Encoding string (default: 'utf-8')
        """
        try:
            with open(file_path, 'rb') as f:
                first_line = f.readline().decode('utf-8', errors='ignore')
                if 'encoding=' in first_line:
                    start = first_line.find('encoding=') + 10
                    end = first_line.find('"', start)
                    if end == -1:
                        end = first_line.find("'", start)
                    return first_line[start:end] if end != -1 else 'utf-8'
        except Exception:
            pass
        return 'utf-8'
    
    @staticmethod
    def pretty_print_xml(xml_content: str) -> str:
        """Format XML content with proper indentation.
        
        Args:
            xml_content: Raw XML content
            
        Returns:
            Pretty-formatted XML string
        """
        try:
            root = ET.fromstring(xml_content)
            return ET.tostring(root, encoding="unicode", pretty_print=True)
        except Exception as e:
            raise ValueError(f"Failed to format XML: {str(e)}")


class XmlSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define text formats for different XML elements
        self.xml_keyword_format = QTextCharFormat()
        self.xml_keyword_format.setForeground(QColor(128, 0, 255))  # Purple for tags
        self.xml_keyword_format.setFontWeight(QFont.Weight.Bold)
        
        self.xml_element_format = QTextCharFormat()
        self.xml_element_format.setForeground(QColor(0, 0, 255))  # Blue for element names
        
        self.xml_attribute_format = QTextCharFormat()
        self.xml_attribute_format.setForeground(QColor(255, 127, 0))  # Orange for attributes
        
        self.xml_value_format = QTextCharFormat()
        self.xml_value_format.setForeground(QColor(0, 128, 0))  # Green for attribute values
        
        self.xml_comment_format = QTextCharFormat()
        self.xml_comment_format.setForeground(QColor(128, 128, 128))  # Gray for comments
        self.xml_comment_format.setFontItalic(True)
        
        self.xml_declaration_format = QTextCharFormat()
        self.xml_declaration_format.setForeground(QColor(255, 0, 255))  # Magenta for XML declaration
        self.xml_declaration_format.setFontWeight(QFont.Weight.Bold)
        
        # Define highlighting rules
        self.highlighting_rules = []
        
        # XML declaration (<?xml ... ?>)
        self.highlighting_rules.append((
            re.compile(r'<\?xml.*?\?>'),
            self.xml_declaration_format
        ))
        
        # XML comments
        self.highlighting_rules.append((
            re.compile(r'<!--.*?-->', re.DOTALL),
            self.xml_comment_format
        ))
        
        # XML tags (opening and closing) - improved pattern
        self.highlighting_rules.append((
            re.compile(r'</?[A-Za-z0-9_:-]+'),
            self.xml_keyword_format
        ))
        
        # Tag closing brackets
        self.highlighting_rules.append((
            re.compile(r'[/>]+>'),
            self.xml_keyword_format
        ))
        
        # XML attributes
        self.highlighting_rules.append((
            re.compile(r'\b[A-Za-z0-9_:-]+(?=\s*=)'),
            self.xml_attribute_format
        ))
        
        # XML attribute values (double quotes)
        self.highlighting_rules.append((
            re.compile(r'"[^"]*"'),
            self.xml_value_format
        ))
        
        # XML attribute values (single quotes)
        self.highlighting_rules.append((
            re.compile(r"'[^']*'"),
            self.xml_value_format
        ))

    def highlightBlock(self, text):
        # Apply each highlighting rule
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class XmlTextEditEnhancer:
    """Helper class to enhance any QTextEdit with XML syntax highlighting."""
    
    def __init__(self, text_edit_widget: QTextEdit):
        """Initialize the enhancer with an existing QTextEdit widget.
        
        Args:
            text_edit_widget: The QTextEdit widget to enhance
        """
        self.text_edit = text_edit_widget
        
        # Apply syntax highlighter
        self.highlighter = XmlSyntaxHighlighter(self.text_edit.document())
        
        # Set a monospace font for better formatting
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        self.text_edit.setFont(font)
        
        # Set some nice defaults for XML editing
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_edit.setAcceptRichText(False)  # Plain text only for proper highlighting


class XmlTextEdit(QTextEdit):
    """Enhanced QTextEdit with XML syntax highlighting and formatting capabilities."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Apply syntax highlighter
        self.highlighter = XmlSyntaxHighlighter(self.document())
        
        # Set a monospace font for better formatting
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        self.setFont(font)
        
        # Set some nice defaults for XML editing
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setAcceptRichText(False)  # Plain text only for proper highlighting
        
    def set_xml_content(self, xml_content: str, pretty_format: bool = True):
        """Set XML content with optional pretty formatting.
        
        Args:
            xml_content: XML content as string
            pretty_format: Whether to apply pretty formatting (default: True)
        """
        try:
            if pretty_format:
                # Use your existing XMLUtils for pretty printing
                formatted_xml = XMLUtils.pretty_print_xml(xml_content)
                self.text_edit.setPlainText(formatted_xml)
            else:
                self.text_edit.setPlainText(xml_content)
        except Exception as e:
            # If formatting fails, just set the original content
            self.text_edit.setPlainText(xml_content)
            print(f"XML formatting error: {e}")
    
    def get_xml_content(self) -> str:
        """Get the current XML content."""
        return self.text_edit.toPlainText()
    
    def validate_current_xml(self) -> tuple[bool, str]:
        """Validate the current XML content.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        return XMLUtils.validate_xml_syntax(self.text_edit.toPlainText())
    
    def format_current_xml(self):
        """Format the current XML content in-place."""
        current_content = self.text_edit.toPlainText()
        if current_content.strip():
            try:
                formatted = XMLUtils.pretty_print_xml(current_content)
                # Preserve cursor position if possible
                cursor = self.text_edit.textCursor()
                position = cursor.position()
                
                self.text_edit.setPlainText(formatted)
                
                # Try to restore cursor position
                cursor.setPosition(min(position, len(formatted)))
                self.text_edit.setTextCursor(cursor)
            except Exception as e:
                print(f"Error formatting XML: {e}")


# Factory function to enhance existing QTextEdit widgets
def enhance_xml_text_edit(text_edit_widget: QTextEdit) -> XmlTextEditEnhancer:
    """Enhance an existing QTextEdit widget with XML syntax highlighting.
    
    Args:
        text_edit_widget: The QTextEdit widget to enhance
        
    Returns:
        XmlTextEditEnhancer instance for additional functionality
    """
    return XmlTextEditEnhancer(text_edit_widget)


# Utility functions for working with UI-created QTextEdit widgets
def set_xml_content_to_widget(text_edit: QTextEdit, xml_content: str, pretty_format: bool = True):
    """Set XML content to any QTextEdit widget with optional formatting.
    
    Args:
        text_edit: The QTextEdit widget
        xml_content: XML content as string
        pretty_format: Whether to apply pretty formatting (default: True)
    """
    try:
        if pretty_format:
            formatted_xml = XMLUtils.pretty_print_xml(xml_content)
            text_edit.setPlainText(formatted_xml)
        else:
            text_edit.setPlainText(xml_content)
    except Exception as e:
        text_edit.setPlainText(xml_content)
        print(f"XML formatting error: {e}")


def apply_xml_highlighting_to_widget(text_edit: QTextEdit) -> XmlSyntaxHighlighter:
    """Apply XML syntax highlighting to any QTextEdit widget.
    
    Args:
        text_edit: The QTextEdit widget to enhance
        
    Returns:
        The XmlSyntaxHighlighter instance (keep reference to prevent garbage collection)
    """
    # Apply syntax highlighter
    highlighter = XmlSyntaxHighlighter(text_edit.document())
    
    # Set monospace font
    font = QFont("Consolas", 10)
    if not font.exactMatch():
        font = QFont("Courier New", 10)
    text_edit.setFont(font)
    
    # Set XML-friendly settings
    text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    text_edit.setAcceptRichText(False)
    
    return highlighter


class XMLParserThread(QRunnable):
    """Worker thread for various XML operations."""
    
    def __init__(self, operation: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        self.signals = XMLParserSignals()
        self.setAutoDelete(True)
        
        # Operation parameters
        self.xml_file_path = kwargs.get('xml_file_path')
        self.xml_content = kwargs.get('xml_content')
        self.namespace_map = kwargs.get('namespace_map', {})
        
    @Slot()
    def run(self):
        """Main execution method that routes to specific operations."""
        try:
            if self.operation == 'parse':
                self._parse_xml()
            elif self.operation == 'analyze':
                self._analyze_structure()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
                
        except Exception as e:
            self.signals.error_occurred.emit("Operation Error", str(e))
    
    def _parse_xml(self):
        """Parse XML file and extract comprehensive information."""
        tree = ET.parse(self.xml_file_path)
        root = tree.getroot()

        xml_string = ET.tostring(root, encoding="unicode", pretty_print=True)

        # Structures for comprehensive and contextual XML info
        tags = set()
        tag_values = set()
        attributes = set()
        attribute_values = set()
        namespaces = set()

        tag_to_values = {}  # e.g., {"author": ["Gambardella, Matthew", "Ralls, Kim", ...]}
        tag_to_attributes = {}  # e.g., {"book": ["id"]}
        tag_attr_to_values = {}  # e.g., {("book", "id"): ["bk101", "bk102", ...]}

        for elem in root.iter():
            tag = elem.tag
            tags.add(tag)

            # Namespace extraction
            if '}' in tag:
                namespace = tag.split('}')[0][1:]
                namespaces.add(namespace)

            # Text content mapping
            if elem.text and elem.text.strip():
                value = elem.text.strip()
                tag_values.add(value)
                tag_to_values.setdefault(tag, set()).add(value)

            # Attributes
            for attr, val in elem.attrib.items():
                attributes.add(attr)
                attribute_values.add(val)
                tag_to_attributes.setdefault(tag, set()).add(attr)
                tag_attr_to_values.setdefault((tag, attr), set()).add(val)

        # Convert sets to sorted lists
        tag_to_values = {k: sorted(v) for k, v in tag_to_values.items()}
        tag_to_attributes = {k: sorted(v) for k, v in tag_to_attributes.items()}
        tag_attr_to_values = {k: sorted(v) for k, v in tag_attr_to_values.items()}

        result = {
            'xml_string': xml_string,
            'tags': sorted(tags),
            'tag_values': sorted(tag_values),
            'attributes': sorted(attributes),
            'attribute_values': sorted(attribute_values),
            'namespaces': sorted(namespaces),
            'file_path': self.xml_file_path,
            'root_tag': root.tag,
            'element_count': len(list(root.iter())),
            'encoding': XMLUtils.get_xml_encoding(self.xml_file_path),
            'tag_to_values': tag_to_values,
            'tag_to_attributes': tag_to_attributes,
            'tag_attr_to_values': tag_attr_to_values,
        }

        self.signals.program_output_progress.emit("XML parsing completed successfully!")
        self.signals.finished.emit(result)

    
    def _analyze_structure(self):
        """Analyze XML document structure and provide detailed statistics."""
        self.signals.program_output_progress.emit("Analyzing XML structure...")
        
        tree = ET.parse(self.xml_file_path)
        root = tree.getroot()
        
        # Comprehensive structure analysis
        element_stats = {}
        depth_levels = {}
        max_depth = 0
        
        def analyze_element(elem, depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            
            tag = elem.tag
            if tag not in element_stats:
                element_stats[tag] = {
                    'count': 0,
                    'has_text': 0,
                    'has_attributes': 0,
                    'has_children': 0,
                    'attributes': set(),
                    'depths': set()
                }
            
            stats = element_stats[tag]
            stats['count'] += 1
            stats['depths'].add(depth)
            
            if elem.text and elem.text.strip():
                stats['has_text'] += 1
            
            if elem.attrib:
                stats['has_attributes'] += 1
                stats['attributes'].update(elem.attrib.keys())
            
            if len(elem) > 0:
                stats['has_children'] += 1
            
            # Track depth distribution
            if depth not in depth_levels:
                depth_levels[depth] = 0
            depth_levels[depth] += 1
            
            # Recurse through children
            for child in elem:
                analyze_element(child, depth + 1)
        
        analyze_element(root)
        
        # Convert sets to lists for JSON serialization
        for tag_stats in element_stats.values():
            tag_stats['attributes'] = sorted(tag_stats['attributes'])
            tag_stats['depths'] = sorted(tag_stats['depths'])
        
        result = {
            'file_path': self.xml_file_path,
            'root_element': root.tag,
            'max_depth': max_depth,
            'total_elements': sum(stats['count'] for stats in element_stats.values()),
            'unique_elements': len(element_stats),
            'element_statistics': element_stats,
            'depth_distribution': depth_levels,
            'namespaces': self._extract_namespaces(root)
        }
        
        self.signals.finished.emit(result)
        self.signals.program_output_progress.emit("Structure analysis completed!")
    
    def _extract_namespaces(self, root):
        """Extract all namespaces used in the document."""
        namespaces = {}
        for elem in root.iter():
            if elem.nsmap:
                namespaces.update(elem.nsmap)
        return namespaces


# Convenience functions for creating threaded operations
def create_xml_parser(xml_file_path: str) -> XMLParserThread:
    """Create a parser thread for basic XML parsing."""
    return XMLParserThread('parse', xml_file_path=xml_file_path)

def create_structure_analyzer(xml_file_path: str) -> XMLParserThread:
    """Create a structure analyzer thread for detailed XML analysis."""
    return XMLParserThread('analyze', xml_file_path=xml_file_path)