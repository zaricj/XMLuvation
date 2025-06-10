# utils/xml_parser.py
from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from lxml import etree as ET
from typing import Dict, List, Optional, Union
import json
from pathlib import Path


class XMLParserSignals(QObject):
    """Signals class for XMLParserThread operations."""
    finished = Signal(dict)
    error_occurred = Signal(str, str)
    progress = Signal(str)
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
        self.signals.progress.emit("Starting XML parsing...")
        
        tree = ET.parse(self.xml_file_path)
        root = tree.getroot()
        
        xml_string = ET.tostring(root, encoding="unicode", pretty_print=True)
        
        self.signals.progress.emit("Extracting XML elements...")
        
        # Extract comprehensive XML information
        tags = set()
        tag_values = set()
        attributes = set()
        attribute_values = set()
        namespaces = set()
        
        for elem in root.iter():
            # Extract tag information
            tag = elem.tag
            tags.add(tag)
            
            # Extract namespace if present
            if '}' in tag:
                namespace = tag.split('}')[0][1:]  # Remove { and }
                namespaces.add(namespace)
            
            # Extract text content
            if elem.text and elem.text.strip():
                tag_values.add(elem.text.strip())
            
            # Extract attributes
            for attr, value in elem.attrib.items():
                attributes.add(attr)
                attribute_values.add(value)
        
        # Build comprehensive result
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
            'encoding': XMLUtils.get_xml_encoding(self.xml_file_path)
        }
        
        self.signals.progress.emit("XML parsing completed successfully!")
        self.signals.finished.emit(result)
    
    def _analyze_structure(self):
        """Analyze XML document structure and provide detailed statistics."""
        self.signals.progress.emit("Analyzing XML structure...")
        
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
        self.signals.progress.emit("Structure analysis completed!")
    
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
