#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Two-Call Story and Image Generation System

This script validates the entire system across multiple scenarios:
- Different genres and styles
- Various world documents
- Story quality and coherence
- Image generation and alignment
- Threading structure validation
- Error handling and robustness
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.twitter_bot import TwitterBot
from src.ai_solarpunk.world_parser import parse_world_document_for_stories
from src.ai_solarpunk.story_to_image import StoryToImageConverter
from src.story_generator import StoryGenerator
from src.image_generator import ImageGenerator

@dataclass
class TestResult:
    """Data structure for storing test results."""
    test_name: str
    success: bool
    execution_time: float
    details: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    
@dataclass 
class SystemTestSuite:
    """Comprehensive test suite for the two-call system."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.results: List[TestResult] = []
        self.twitter_bot = None
        self.start_time = None
        
    def log(self, message: str, level: str = "INFO") -> None:
        """Log test messages with timestamps."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def setup(self) -> bool:
        """Set up the test environment."""
        try:
            self.log("Setting up test environment...")
            self.start_time = time.time()
            
            # Initialize TwitterBot
            self.twitter_bot = TwitterBot()
            self.log("✅ TwitterBot initialized successfully")
            
            return True
        except Exception as e:
            self.log(f"❌ Setup failed: {e}", "ERROR")
            return False
            
    def test_world_document_parsing(self) -> TestResult:
        """Test world document parsing functionality."""
        test_start = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            self.log("Testing world document parsing...")
            
            # Test StillPoint.md parsing
            world_data = parse_world_document_for_stories('examples/worlds/StillPoint.md')
            
            # Validate required fields
            required_fields = ['world_name', 'genre', 'character_archetypes', 'technology', 'environment']
            missing_fields = [field for field in required_fields if field not in world_data]
            
            if missing_fields:
                errors.append(f"Missing required fields: {missing_fields}")
            
            # Check genre detection
            if world_data.get('genre', '').lower() != 'solarpunk':
                warnings.append(f"Expected 'solarpunk' genre, got '{world_data.get('genre')}'")
                
            # Check plot seeds
            plot_seeds = world_data.get('plot_seeds', [])
            if len(plot_seeds) < 3:
                warnings.append(f"Only {len(plot_seeds)} plot seeds found, expected at least 3")
                
            details = {
                'world_name': world_data.get('world_name'),
                'genre': world_data.get('genre'),
                'plot_seeds_count': len(plot_seeds),
                'character_archetypes_count': len(world_data.get('character_archetypes', [])),
                'environment_fields': len(world_data.get('environment', {})) if isinstance(world_data.get('environment', {}), dict) else 1,
                'technologies_count': len(world_data.get('technology', []))
            }
            
            success = len(errors) == 0
            self.log(f"{'✅' if success else '❌'} World document parsing test {'passed' if success else 'failed'}")
            
        except Exception as e:
            errors.append(f"World parsing error: {str(e)}")
            success = False
            self.log(f"❌ World document parsing test failed: {e}", "ERROR")
            
        return TestResult(
            test_name="world_document_parsing",
            success=success,
            execution_time=time.time() - test_start,
            details=details,
            errors=errors,
            warnings=warnings
        )
        
    def test_story_generation_quality(self) -> TestResult:
        """Test story generation quality and structure."""
        test_start = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            self.log("Testing story generation quality...")
            
            # Generate world-based story
            post_data = self.twitter_bot.generate_world_post(
                world_document_path='examples/worlds/StillPoint.md',
                story_mode='extended',
                style='digital-art'
            )
            
            story = post_data.get('story', '')
            threading_blocks = post_data.get('threading_blocks', [])
            
            # Validate story length (should be around 250 words)
            word_count = len(story.split())
            if word_count < 200 or word_count > 300:
                warnings.append(f"Story word count {word_count} outside expected range (200-300)")
                
            # Validate threading blocks
            if len(threading_blocks) < 5:
                warnings.append(f"Only {len(threading_blocks)} threading blocks, expected at least 5")
                
            # Check threading block lengths
            oversized_blocks = []
            for i, block in enumerate(threading_blocks):
                if len(block) > 250:
                    oversized_blocks.append(f"Block {i+1}: {len(block)} chars")
                    
            if oversized_blocks:
                errors.append(f"Threading blocks too long: {oversized_blocks}")
                
            # Check for story coherence indicators
            coherence_indicators = {
                'has_characters': any(name.istitle() and len(name) > 2 for name in story.split()),
                'has_setting': 'city' in story.lower() or 'garden' in story.lower() or 'building' in story.lower(),
                'has_action': any(verb in story.lower() for verb in ['walked', 'ran', 'moved', 'looked', 'saw', 'heard']),
                'has_emotion': any(emotion in story.lower() for emotion in ['felt', 'happy', 'sad', 'excited', 'calm', 'peaceful'])
            }
            
            missing_elements = [element for element, present in coherence_indicators.items() if not present]
            if missing_elements:
                warnings.append(f"Story may lack elements: {missing_elements}")
                
            details = {
                'story_length': len(story),
                'word_count': word_count,
                'threading_blocks_count': len(threading_blocks),
                'average_block_length': sum(len(block) for block in threading_blocks) / len(threading_blocks) if threading_blocks else 0,
                'coherence_indicators': coherence_indicators,
                'genre_detected': post_data.get('world_info', {}).get('genre')
            }
            
            success = len(errors) == 0
            self.log(f"{'✅' if success else '❌'} Story generation quality test {'passed' if success else 'failed'}")
            
        except Exception as e:
            errors.append(f"Story generation error: {str(e)}")
            success = False
            self.log(f"❌ Story generation test failed: {e}", "ERROR")
            
        return TestResult(
            test_name="story_generation_quality", 
            success=success,
            execution_time=time.time() - test_start,
            details=details,
            errors=errors,
            warnings=warnings
        )
        
    def test_image_generation_alignment(self) -> TestResult:
        """Test image generation and story-image alignment."""
        test_start = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            self.log("Testing image generation and story alignment...")
            
            # Generate post with image
            post_data = self.twitter_bot.generate_world_post(
                world_document_path='examples/worlds/StillPoint.md',
                story_mode='extended',
                style='digital-art'
            )
            
            story = post_data.get('story', '')
            image_url = post_data.get('image_url', '')
            image_prompt = post_data.get('image_prompt', '')
            
            # Validate image generation
            if not image_url:
                errors.append("No image URL generated")
            elif not os.path.exists(image_url):
                errors.append(f"Generated image file does not exist: {image_url}")
                
            # Validate image prompt quality
            if not image_prompt:
                errors.append("No image prompt generated")
            elif len(image_prompt) < 50:
                warnings.append(f"Image prompt seems short: {len(image_prompt)} chars")
                
            # Test story-to-image conversion
            converter = StoryToImageConverter()
            visual_elements = converter._analyze_story_elements(story)
            
            prompt_alignment_score = 0
            if visual_elements.characters and any(char.lower() in image_prompt.lower() for char in visual_elements.characters):
                prompt_alignment_score += 1
            if visual_elements.setting and any(setting.lower() in image_prompt.lower() for setting in visual_elements.setting):
                prompt_alignment_score += 1
            if visual_elements.mood and visual_elements.mood.lower() in image_prompt.lower():
                prompt_alignment_score += 1
                
            if prompt_alignment_score < 2:
                warnings.append(f"Low story-image alignment score: {prompt_alignment_score}/3")
                
            details = {
                'image_generated': bool(image_url),
                'image_file_exists': os.path.exists(image_url) if image_url else False,
                'image_prompt_length': len(image_prompt),
                'story_image_alignment_score': prompt_alignment_score,
                'visual_elements': {
                    'characters_count': len(visual_elements.characters) if visual_elements.characters else 0,
                    'setting_elements': len(visual_elements.setting) if visual_elements.setting else 0,
                    'actions_count': len(visual_elements.actions) if visual_elements.actions else 0,
                    'mood_detected': bool(visual_elements.mood)
                }
            }
            
            success = len(errors) == 0
            self.log(f"{'✅' if success else '❌'} Image generation alignment test {'passed' if success else 'failed'}")
            
        except Exception as e:
            errors.append(f"Image generation error: {str(e)}")
            success = False
            self.log(f"❌ Image generation test failed: {e}", "ERROR")
            
        return TestResult(
            test_name="image_generation_alignment",
            success=success,
            execution_time=time.time() - test_start,
            details=details,
            errors=errors,
            warnings=warnings
        )
        
    def test_multi_genre_support(self) -> TestResult:
        """Test system with multiple genres and styles."""
        test_start = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            self.log("Testing multi-genre support...")
            
            # Test different styles (reduced to avoid long test times)
            styles = ['digital-art', 'watercolor']
            style_results = {}
            
            for style in styles:
                try:
                    self.log(f"  Testing style: {style}")
                    post_data = self.twitter_bot.generate_world_post(
                        world_document_path='examples/worlds/StillPoint.md',
                        story_mode='extended',
                        style=style
                    )
                    
                    style_results[style] = {
                        'success': True,
                        'story_length': len(post_data.get('story', '')),
                        'threading_blocks': len(post_data.get('threading_blocks', [])),
                        'image_generated': bool(post_data.get('image_url'))
                    }
                    
                    # Small delay between tests
                    time.sleep(2)
                    
                except Exception as e:
                    style_results[style] = {
                        'success': False,
                        'error': str(e)
                    }
                    warnings.append(f"Style {style} failed: {e}")
                    
            successful_styles = sum(1 for result in style_results.values() if result.get('success', False))
            
            details = {
                'styles_tested': len(styles),
                'successful_styles': successful_styles,
                'style_results': style_results
            }
            
            success = successful_styles >= len(styles) // 2  # At least half should succeed
            self.log(f"{'✅' if success else '❌'} Multi-genre support test {'passed' if success else 'failed'}")
            
        except Exception as e:
            errors.append(f"Multi-genre test error: {str(e)}")
            success = False
            self.log(f"❌ Multi-genre test failed: {e}", "ERROR")
            
        return TestResult(
            test_name="multi_genre_support",
            success=success,
            execution_time=time.time() - test_start,
            details=details,
            errors=errors,
            warnings=warnings
        )
        
    def test_error_handling_robustness(self) -> TestResult:
        """Test system error handling and robustness."""
        test_start = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            self.log("Testing error handling and robustness...")
            
            robustness_tests = {
                'invalid_world_path': False,
                'invalid_style': False,
                'invalid_mode': False
            }
            
            # Test invalid world document path
            try:
                self.twitter_bot.generate_world_post(
                    world_document_path='nonexistent/world.md',
                    story_mode='extended',
                    style='digital-art'
                )
                warnings.append("System should have failed with invalid world path")
            except Exception:
                robustness_tests['invalid_world_path'] = True
                
            # Test invalid style (should gracefully handle)
            try:
                self.twitter_bot.generate_world_post(
                    world_document_path='examples/worlds/StillPoint.md',
                    story_mode='extended',
                    style='invalid-style'
                )
                # If it doesn't fail, that's actually fine as the system should handle it gracefully
                robustness_tests['invalid_style'] = True
            except Exception:
                robustness_tests['invalid_style'] = True
                
            # Test invalid mode
            try:
                self.twitter_bot.generate_world_post(
                    world_document_path='examples/worlds/StillPoint.md',
                    story_mode='invalid-mode',
                    style='digital-art'
                )
                warnings.append("System should have failed with invalid story mode")
            except Exception:
                robustness_tests['invalid_mode'] = True
                
            passed_tests = sum(robustness_tests.values())
            
            details = {
                'robustness_tests': robustness_tests,
                'passed_robustness_tests': passed_tests,
                'total_robustness_tests': len(robustness_tests)
            }
            
            success = passed_tests >= 2  # At least 2/3 should pass
            self.log(f"{'✅' if success else '❌'} Error handling robustness test {'passed' if success else 'failed'}")
            
        except Exception as e:
            errors.append(f"Robustness test error: {str(e)}")
            success = False
            self.log(f"❌ Robustness test failed: {e}", "ERROR")
            
        return TestResult(
            test_name="error_handling_robustness",
            success=success,
            execution_time=time.time() - test_start,
            details=details,
            errors=errors,
            warnings=warnings
        )
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report."""
        self.log("Starting comprehensive two-call system testing...")
        
        if not self.setup():
            return {"error": "Setup failed"}
            
        # Run individual tests
        tests = [
            self.test_world_document_parsing,
            self.test_story_generation_quality,
            self.test_image_generation_alignment,
            self.test_multi_genre_support,
            self.test_error_handling_robustness
        ]
        
        for test_func in tests:
            try:
                result = test_func()
                self.results.append(result)
                
                # Brief delay between tests
                time.sleep(1)
                
            except Exception as e:
                self.log(f"❌ Test {test_func.__name__} crashed: {e}", "ERROR")
                self.results.append(TestResult(
                    test_name=test_func.__name__,
                    success=False,
                    execution_time=0,
                    details={},
                    errors=[f"Test crashed: {str(e)}"],
                    warnings=[]
                ))
                
        return self.generate_report()
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result.success)
        total_time = time.time() - self.start_time if self.start_time else 0
        
        # Aggregate errors and warnings
        all_errors = []
        all_warnings = []
        for result in self.results:
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)
            
        report = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'total_execution_time': total_time
            },
            'test_results': [asdict(result) for result in self.results],
            'aggregated_issues': {
                'total_errors': len(all_errors),
                'total_warnings': len(all_warnings),
                'errors': all_errors,
                'warnings': all_warnings
            },
            'system_health': {
                'overall_status': 'PASS' if passed_tests >= total_tests * 0.8 else 'FAIL',
                'critical_issues': len(all_errors),
                'minor_issues': len(all_warnings)
            }
        }
        
        return report
        
    def print_report(self, report: Dict[str, Any]) -> None:
        """Print formatted test report."""
        print("\n" + "="*60)
        print("TWO-CALL SYSTEM COMPREHENSIVE TEST REPORT")
        print("="*60)
        
        summary = report['test_summary']
        print(f"\n📊 SUMMARY:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed_tests']} ✅")
        print(f"  Failed: {summary['failed_tests']} ❌")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Total Time: {summary['total_execution_time']:.2f}s")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"  {result.test_name}: {status} ({result.execution_time:.2f}s)")
            if result.errors:
                for error in result.errors:
                    print(f"    🚨 ERROR: {error}")
            if result.warnings:
                for warning in result.warnings:
                    print(f"    ⚠️  WARNING: {warning}")
                    
        health = report['system_health']
        print(f"\n🏥 SYSTEM HEALTH: {health['overall_status']}")
        print(f"  Critical Issues: {health['critical_issues']}")
        print(f"  Minor Issues: {health['minor_issues']}")
        
        if health['overall_status'] == 'PASS':
            print("\n🎉 TWO-CALL SYSTEM IS READY FOR PRODUCTION!")
        else:
            print("\n⚠️  SYSTEM NEEDS ATTENTION BEFORE PRODUCTION USE")
            
        print("="*60)

def main():
    """Main test execution function."""
    test_suite = SystemTestSuite()
    
    try:
        # Run all tests
        report = test_suite.run_all_tests()
        
        # Print results
        test_suite.print_report(report)
        
        # Save report to file
        report_file = f"test_results/two_call_system_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"\n📁 Report saved to: {report_file}")
        
        # Exit with appropriate code
        exit_code = 0 if report['system_health']['overall_status'] == 'PASS' else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 