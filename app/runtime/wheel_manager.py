"""
WheelManager: Core component for managing wheel files and plugin discovery.
Loads wheels, discovers plugin entry points, imports modules, locates metadata,
and holds PluginDescriptors.
"""

import os
import sys
import importlib
import importlib.util
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
import logging

from app.lib.wheel_entry import Wheel
from app.runtime.plugin_descriptor import PluginDescriptor
from app.runtime.schema_loader import SchemaLoader
from hiagent_plugin_sdk.schema import Metadata

logger = logging.getLogger(__name__)


class WheelManager:
    """
    Manages wheel files and plugin discovery.
    
    Responsibilities:
    - Load wheel files and extract metadata
    - Discover plugin entry points from wheels
    - Import plugin modules dynamically
    - Create and manage PluginDescriptor instances
    - Maintain registry of loaded plugins
    """
    
    def __init__(self, wheel_directory: Optional[str] = None):
        """
        Initialize WheelManager.
        
        Args:
            wheel_directory: Directory containing wheel files. If None, uses current directory.
        """
        self.wheel_directory = Path(wheel_directory or os.getcwd())
        self.loaded_wheels: Dict[str, Wheel] = {}
        self.plugin_descriptors: Dict[str, PluginDescriptor] = {}
        self.schema_loader = SchemaLoader()
        
        # Track imported modules to avoid conflicts
        self._imported_modules: Dict[str, Any] = {}
        
    def discover_wheels(self, pattern: str = "*.whl") -> List[Path]:
        """
        Discover all wheel files in the configured directory.
        
        Args:
            pattern: File pattern to match (default: "*.whl")
            
        Returns:
            List of Path objects pointing to wheel files
        """
        try:
            wheel_files = list(self.wheel_directory.glob(pattern))
            logger.info(f"Discovered {len(wheel_files)} wheel files in {self.wheel_directory}")
            return wheel_files
        except Exception as e:
            logger.error(f"Failed to discover wheels: {e}")
            return []
    
    def load_wheel(self, wheel_path: Path) -> Optional[Wheel]:
        """
        Load a single wheel file.
        
        Args:
            wheel_path: Path to the wheel file
            
        Returns:
            Loaded Wheel object or None if loading failed
        """
        try:
            wheel = Wheel(str(wheel_path))
            wheel.read()  # Initialize the wheel metadata
            
            wheel_key = f"{wheel.name}-{wheel.version}"
            self.loaded_wheels[wheel_key] = wheel
            
            logger.info(f"Loaded wheel: {wheel_key}")
            return wheel
        except Exception as e:
            logger.error(f"Failed to load wheel {wheel_path}: {e}")
            return None
    
    def discover_plugin_entry_points(self, wheel: Wheel) -> Dict[str, str]:
        """
        Discover plugin entry points from a wheel.
        
        Args:
            wheel: Loaded wheel object
            
        Returns:
            Dictionary mapping plugin names to entry point strings
        """
        try:
            entry_points = wheel.entry_points
            
            # Look for hiagent plugin entry points
            plugin_entries = {}
            
            # Check for 'hiagent_plugins' entry point group
            if 'hiagent_plugins' in entry_points:
                for entry_point in entry_points['hiagent_plugins']:
                    plugin_entries[entry_point.name] = entry_point.value
            
            # Fallback: check for other common entry point names
            for group_name in ['plugins', 'hiagent.plugins']:
                if group_name in entry_points:
                    for entry_point in entry_points[group_name]:
                        plugin_entries[entry_point.name] = entry_point.value
            
            logger.info(f"Discovered {len(plugin_entries)} plugin entry points in {wheel.name}")
            return plugin_entries
            
        except Exception as e:
            logger.error(f"Failed to discover entry points from wheel {wheel.name}: {e}")
            return {}
    
    def import_plugin_module(self, entry_point: str, wheel_path: Path) -> Optional[Any]:
        """
        Import a plugin module from an entry point.
        
        Args:
            entry_point: Entry point string (e.g., "module.path:ClassName")
            wheel_path: Path to the wheel file
            
        Returns:
            Imported plugin class or None if import failed
        """
        try:
            # Parse entry point: "module.path:ClassName"
            if ':' not in entry_point:
                logger.error(f"Invalid entry point format: {entry_point}")
                return None
            
            module_path, class_name = entry_point.split(':', 1)
            
            # Check if module is already imported
            module_key = f"{wheel_path.name}:{module_path}"
            if module_key in self._imported_modules:
                module = self._imported_modules[module_key]
            else:
                # Add wheel to sys.path temporarily for import
                wheel_dir = str(wheel_path.parent)
                if wheel_dir not in sys.path:
                    sys.path.insert(0, wheel_dir)
                
                try:
                    # Import the module
                    module = importlib.import_module(module_path)
                    self._imported_modules[module_key] = module
                finally:
                    # Clean up sys.path
                    if wheel_dir in sys.path:
                        sys.path.remove(wheel_dir)
            
            # Get the plugin class
            plugin_class = getattr(module, class_name)
            logger.info(f"Successfully imported plugin class: {class_name} from {module_path}")
            return plugin_class
            
        except Exception as e:
            logger.error(f"Failed to import plugin from entry point {entry_point}: {e}")
            return None
    
    def create_plugin_descriptor(
        self, 
        plugin_name: str, 
        plugin_class: Type[Any], 
        metadata: Metadata,
        wheel: Wheel
    ) -> Optional[PluginDescriptor]:
        """
        Create a PluginDescriptor for a discovered plugin.
        
        Args:
            plugin_name: Name of the plugin
            plugin_class: Imported plugin class
            metadata: Plugin metadata
            wheel: Source wheel object
            
        Returns:
            Created PluginDescriptor or None if creation failed
        """
        try:
            descriptor = PluginDescriptor(
                name=plugin_name,
                plugin_class=plugin_class,
                metadata=metadata,
                wheel_info={
                    'name': wheel.name,
                    'version': wheel.version,
                    'filename': wheel.filename
                }
            )
            
            self.plugin_descriptors[plugin_name] = descriptor
            logger.info(f"Created plugin descriptor for: {plugin_name}")
            return descriptor
            
        except Exception as e:
            logger.error(f"Failed to create plugin descriptor for {plugin_name}: {e}")
            return None
    
    def load_all_plugins(self) -> Dict[str, PluginDescriptor]:
        """
        Discover and load all plugins from wheels in the configured directory.
        
        Returns:
            Dictionary mapping plugin names to PluginDescriptor instances
        """
        logger.info("Starting plugin discovery and loading process")
        
        # Discover all wheel files
        wheel_files = self.discover_wheels()
        
        for wheel_path in wheel_files:
            try:
                # Load the wheel
                wheel = self.load_wheel(wheel_path)
                if not wheel:
                    continue
                
                # Extract metadata
                metadata = wheel.extract_metadata()
                if not metadata:
                    logger.warning(f"No metadata found in wheel: {wheel_path.name}")
                    continue
                
                # Discover plugin entry points
                entry_points = self.discover_plugin_entry_points(wheel)
                
                for plugin_name, entry_point in entry_points.items():
                    # Import plugin module
                    plugin_class = self.import_plugin_module(entry_point, wheel_path)
                    if not plugin_class:
                        continue
                    
                    # Create plugin descriptor
                    self.create_plugin_descriptor(
                        plugin_name, 
                        plugin_class, 
                        metadata, 
                        wheel
                    )
                    
            except Exception as e:
                logger.error(f"Failed to process wheel {wheel_path}: {e}")
                continue
        
        logger.info(f"Loaded {len(self.plugin_descriptors)} plugins total")
        return self.plugin_descriptors.copy()
    
    def get_plugin_descriptor(self, plugin_name: str) -> Optional[PluginDescriptor]:
        """
        Get a specific plugin descriptor by name.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            PluginDescriptor or None if not found
        """
        return self.plugin_descriptors.get(plugin_name)
    
    def get_all_plugin_descriptors(self) -> Dict[str, PluginDescriptor]:
        """
        Get all loaded plugin descriptors.
        
        Returns:
            Dictionary mapping plugin names to PluginDescriptor instances
        """
        return self.plugin_descriptors.copy()
    
    def reload_plugin(self, plugin_name: str) -> Optional[PluginDescriptor]:
        """
        Reload a specific plugin by name.
        
        Args:
            plugin_name: Name of the plugin to reload
            
        Returns:
            Reloaded PluginDescriptor or None if reload failed
        """
        try:
            # Remove existing descriptor
            if plugin_name in self.plugin_descriptors:
                old_descriptor = self.plugin_descriptors[plugin_name]
                # Clean up any existing instance
                if old_descriptor.instance:
                    del old_descriptor.instance
                del self.plugin_descriptors[plugin_name]
            
            # Clear imported modules cache for this plugin
            keys_to_remove = [k for k in self._imported_modules.keys() if plugin_name in k]
            for key in keys_to_remove:
                del self._imported_modules[key]
            
            # Reload all plugins (simpler approach)
            self.load_all_plugins()
            
            return self.plugin_descriptors.get(plugin_name)
            
        except Exception as e:
            logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources and close wheel files."""
        try:
            # Close all wheel files
            for wheel in self.loaded_wheels.values():
                if hasattr(wheel, 'reader') and wheel.reader:
                    wheel.reader.close()
            
            # Clear all caches
            self.loaded_wheels.clear()
            self.plugin_descriptors.clear()
            self._imported_modules.clear()
            
            logger.info("WheelManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during WheelManager cleanup: {e}")
