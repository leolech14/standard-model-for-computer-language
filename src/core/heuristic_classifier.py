#!/usr/bin/env python3
"""
🔬 Auto Pattern Discovery Engine

Deterministic pattern discovery applied during pipeline execution.
Discovers and exposes naming patterns that can become new atom types.
"""

from typing import Dict, List, Tuple, Counter
from collections import Counter, defaultdict
import re


class HeuristicClassifier:
    """
    Deterministic naming pattern classifier (Tier 3).
    Acts as a fallback when topological and inheritance extraction fail.
    """
    
    # Prefix patterns to detect
    PREFIX_ROLES = {
        'test_': 'Test',
        'get_': 'Query',
        'set_': 'Command',
        'add_': 'Command',
        'remove_': 'Command',
        'delete_': 'Command',
        'update_': 'Command',
        'create_': 'Factory',
        'build_': 'Factory',
        'make_': 'Factory',
        'find_': 'Query',
        'fetch_': 'Query',
        'load_': 'Query',
        'save_': 'Command',
        'is_': 'Specification',
        'has_': 'Specification',
        'can_': 'Specification',
        'should_': 'Specification',
        'validate_': 'Validator',
        'check_': 'Validator',
        'parse_': 'Utility',
        'format_': 'Utility',
        'convert_': 'Mapper',
        'transform_': 'Mapper',
        'to_': 'Mapper', 
        'from_': 'Factory',
        'as_': 'Mapper',
        'handle_': 'EventHandler',
        'on_': 'EventHandler',
        'do_': 'Command',
        'run_': 'Command',
        'execute_': 'UseCase',
        'process_': 'Service',
        'render_': 'Utility',
        'init_': 'Service',
        'setup_': 'Service',
        'teardown_': 'Service',
        'cleanup_': 'Service',
    }
    
    # Suffix patterns
    SUFFIX_ROLES = {
        '_handler': 'EventHandler',
        '_callback': 'EventHandler',
        '_hook': 'EventHandler',
        '_validator': 'Validator',
        '_factory': 'Factory',
        '_builder': 'Builder',
        '_service': 'Service',
        '_helper': 'Utility',
        '_util': 'Utility',
        '_utils': 'Utility',
        '_manager': 'Service',
        '_processor': 'Service',
        '_parser': 'Utility',
        '_serializer': 'Mapper',
        '_deserializer': 'Mapper',
        '_converter': 'Mapper',
        '_adapter': 'Adapter',
        '_decorator': 'Utility',
        '_wrapper': 'Utility',
        '_mixin': 'Utility',
        '_test': 'Test',
        '_spec': 'Specification',
        # Java conventions (camelCase)
        'Service': 'Service',
        'Repository': 'Repository',
        'Controller': 'Controller',
        'Handler': 'EventHandler',
        'Factory': 'Factory',
        'Builder': 'Builder',
        'Mapper': 'Mapper',
        'Validator': 'Validator',
        'Provider': 'Provider',
        'Client': 'Client',
        'Impl': 'RepositoryImpl',
        # Go conventions
        'Handler': 'EventHandler',
        'Middleware': 'Service',
    }
    
    # Java/TypeScript prefix patterns (for polyglot support)
    JAVA_TS_PREFIX_ROLES = {
        # Java test patterns
        'test': 'Test',       # testUserLogin
        'should': 'Test',     # shouldReturnUser
        'given': 'Test',      # givenValidInput
        'when': 'Test',       # whenUserLogsIn
        'then': 'Test',       # thenReturnSuccess
        # TypeScript/Jest patterns  
        'describe': 'Test',   # describe('UserService')
        'it': 'Test',         # it('should work')
        'expect': 'Validator',
        'beforeEach': 'Fixture',
        'afterEach': 'Fixture',
        'beforeAll': 'Fixture',
        'afterAll': 'Fixture',
        # Go patterns
        'Test': 'Test',       # TestUserLogin
        'Benchmark': 'Test',  # BenchmarkSort
        'Example': 'Test',    # ExampleSort
        # Angular/NestJS
        'ng': 'Service',      # ngOnInit
        '@Injectable': 'Service',
        '@Component': 'Controller',
        '@Pipe': 'Mapper',
        '@Directive': 'Service',
        '@Service': 'Service',
        '@Repository': 'Repository',
        '@Controller': 'Controller',
        '@Test': 'Test',
    }
    
    # Dunder methods
    DUNDER_ROLES = {
        '__init__': 'Lifecycle',
        '__new__': 'Factory',
        '__del__': 'Lifecycle',
        '__str__': 'Utility',
        '__repr__': 'Utility',
        '__eq__': 'Specification',
        '__ne__': 'Specification',
        '__lt__': 'Specification',
        '__le__': 'Specification',
        '__gt__': 'Specification',
        '__ge__': 'Specification',
        '__hash__': 'Utility',
        '__bool__': 'Specification',
        '__len__': 'Query',
        '__iter__': 'Iterator',
        '__next__': 'Iterator',
        '__getitem__': 'Query',
        '__setitem__': 'Command',
        '__delitem__': 'Command',
        '__contains__': 'Specification',
        '__call__': 'Command',
        '__enter__': 'Lifecycle',
        '__exit__': 'Lifecycle',
        '__getattr__': 'Query',
        '__setattr__': 'Command',
    }

    def __init__(self):
        self.discovered_patterns: Dict[str, int] = Counter()
        self.unknown_names: List[str] = []
    
    def classify_by_pattern(self, name: str) -> Tuple[str, float]:
        """
        Deterministically classify a function/method name by pattern.
        Returns (type, confidence).
        """
        if not name:
            return ('Unknown', 0.0)
        
        # Get the short name (last part after dot)
        short = name.split('.')[-1] if '.' in name else name
        short_lower = short.lower()
        full_name_lower = name.lower()
        
        # 0. TEST CONTEXT DETECTION (highest priority after dunders)
        # Check if this is in a test context based on:
        # - Full name contains "Test" (class name)
        # - Full name contains "test_" anywhere
        # - Name ends with "_test" or "_tests"
        # - File path would contain "test" (handled separately)
        if any(pattern in full_name_lower for pattern in ['test.', '.test', 'test_', '_test', 'tests.', '.tests']):
            self.discovered_patterns['test_context'] += 1
            return ('Test', 90.0)
        
        # 1. Check dunder methods (highest confidence)
        if short_lower.startswith('__') and short_lower.endswith('__'):
            for dunder, role in self.DUNDER_ROLES.items():
                if short_lower == dunder:
                    return (role, 95.0)
            # Unknown dunder
            return ('Utility', 70.0)
        
        # 2. Check prefix patterns
        for prefix, role in self.PREFIX_ROLES.items():
            if short_lower.startswith(prefix):
                self.discovered_patterns[f'prefix:{prefix}'] += 1
                return (role, 85.0)
        
        # 2.5 Check Java/TypeScript/Go patterns (camelCase prefixes)
        for prefix, role in self.JAVA_TS_PREFIX_ROLES.items():
            # Check exact match for short names
            if short == prefix or short_lower == prefix.lower():
                self.discovered_patterns[f'java_ts:{prefix}'] += 1
                return (role, 85.0)
            # Check camelCase prefix (e.g., testUserLogin, shouldReturnUser)
            if short.startswith(prefix) and len(short) > len(prefix):
                next_char = short[len(prefix)]
                if next_char.isupper() or next_char == '_':
                    self.discovered_patterns[f'java_ts:{prefix}'] += 1
                    return (role, 80.0)        
        # 3. Check suffix patterns (both lowercase and original case)
        for suffix, role in self.SUFFIX_ROLES.items():
            # Check lowercase suffix
            if short_lower.endswith(suffix.lower()):
                self.discovered_patterns[f'suffix:{suffix}'] += 1
                return (role, 85.0)
            # Check original case suffix (e.g., UserService)
            if short.endswith(suffix):
                self.discovered_patterns[f'suffix:{suffix}'] += 1
                return (role, 85.0)
        
        # 4. Private methods (single underscore prefix)
        if short_lower.startswith('_') and not short_lower.startswith('__'):
            self.discovered_patterns['_private'] += 1
            return ('Internal', 70.0)
        
        # 5. Entry points / main entry
        if short_lower in ('index', 'main', 'app', 'application', 'root', 'home', 'default'):
            self.discovered_patterns['entry_point'] += 1
            return ('Controller', 75.0)
        
        # 6. Fixture/Example patterns (common in framework docs/tests)
        # IMPORTANT: Only match if NOT also matching a suffix pattern (e.g., UserService)
        fixture_tokens = {'fake', 'mock', 'stub', 'dummy', 'sample', 'example', 'demo', 
                         'fixture', 'hero', 'item', 'todo', 'post', 'comment'}
        # Remove 'user' from here - too common in real class names
        is_fixture = any(token in short_lower for token in fixture_tokens)
        # Check if it's actually a domain class pattern
        has_domain_suffix = any(short.endswith(s) for s in ['Service', 'Repository', 'Controller', 'Handler', 'Factory', 'Builder', 'Mapper', 'Validator'])
        if is_fixture and not has_domain_suffix:
            self.discovered_patterns['fixture/example'] += 1
            return ('Fixture', 70.0)
        
        # 7. Common framework patterns
        if any(x in short_lower for x in ['endpoint', 'route', 'view', 'page']):
            self.discovered_patterns['endpoint'] += 1
            return ('Controller', 75.0)
        
        # 8. Data operations
        if any(x in short_lower for x in ['decode', 'encode', 'serialize', 'deserialize', 'dump', 'load']):
            self.discovered_patterns['data_ops'] += 1
            return ('Mapper', 75.0)
        
        # 9. Session/state management
        if any(x in short_lower for x in ['session', 'state', 'context', 'scope']):
            self.discovered_patterns['state_mgmt'] += 1
            return ('Service', 70.0)
        
        # 10. Common verbs that are typically Commands
        if any(x in short_lower for x in ['login', 'logout', 'register', 'submit', 'send', 'publish', 'emit']):
            self.discovered_patterns['action_verb'] += 1
            return ('Command', 75.0)
        
        # 11. Common verbs that are typically Queries
        if any(x in short_lower for x in ['read', 'retrieve', 'search', 'lookup', 'resolve']):
            self.discovered_patterns['query_verb'] += 1
            return ('Query', 75.0)
        
        # 12. Collector/aggregator patterns
        if any(x in short_lower for x in ['collect', 'gather', 'aggregate', 'combine', 'merge']):
            self.discovered_patterns['aggregator'] += 1
            return ('Service', 70.0)
        
        # 13. Output/display patterns
        if any(x in short_lower for x in ['print', 'display', 'show', 'output', 'terminal', 'console']):
            self.discovered_patterns['output'] += 1
            return ('Utility', 70.0)
        
        # 14. Flush/sync patterns
        if any(x in short_lower for x in ['flush', 'sync', 'commit', 'persist', 'write']):
            self.discovered_patterns['persist'] += 1
            return ('Command', 75.0)
        
        # ========== NEW PATTERNS FOR 100% COVERAGE ==========
        
        # 15. Database/DB patterns
        if any(x in short_lower for x in ['database', 'db', 'sql', 'query', 'cursor', 'connection', 'pool']):
            self.discovered_patterns['database'] += 1
            return ('Repository', 75.0)
        
        # 16. Schema/Migration patterns  
        if any(x in short_lower for x in ['schema', 'migration', 'upgrade', 'downgrade', 'migrate', 'revision']):
            self.discovered_patterns['migration'] += 1
            return ('Command', 75.0)
        
        # 17. Introspection/Reflection patterns
        if any(x in short_lower for x in ['introspect', 'reflect', 'inspect', 'meta', 'describe']):
            self.discovered_patterns['introspection'] += 1
            return ('Query', 75.0)
        
        # 18. Visitor pattern
        if any(x in short_lower for x in ['visit', 'visitor', 'walk', 'traverse', 'accept']):
            self.discovered_patterns['visitor'] += 1
            return ('Service', 75.0)
        
        # 19. Widget/Input/UI patterns
        if any(x in short_lower for x in ['widget', 'input', 'button', 'slider', 'select', 'checkbox', 
                                           'radio', 'dropdown', 'picker', 'chooser', 'selector']):
            self.discovered_patterns['widget'] += 1
            return ('Controller', 75.0)
        
        # 20. Dialog/Modal/Popup patterns
        if any(x in short_lower for x in ['dialog', 'modal', 'popup', 'overlay', 'toast', 'alert', 'confirm']):
            self.discovered_patterns['dialog'] += 1
            return ('Controller', 75.0)
        
        # 21. Property/Attribute patterns
        if any(x in short_lower for x in ['property', 'prop', 'attribute', 'attr', 'value', 'field']):
            self.discovered_patterns['property'] += 1
            return ('Query', 70.0)
        
        # 22. URL/Path/Route patterns
        if any(x in short_lower for x in ['url', 'path', 'uri', 'link', 'href', 'redirect']):
            self.discovered_patterns['url'] += 1
            return ('Query', 70.0)
        
        # 23. Clear/Reset/Cleanup patterns
        if any(x in short_lower for x in ['clear', 'reset', 'clean', 'purge', 'wipe', 'remove_all']):
            self.discovered_patterns['cleanup'] += 1
            return ('Command', 75.0)
        
        # 24. Error/Exception/Not Found patterns
        if any(x in short_lower for x in ['error', 'exception', 'not_found', 'missing', 'invalid', 'fail']):
            self.discovered_patterns['error'] += 1
            return ('Exception', 75.0)
        
        # 25. Mixin patterns
        if 'mixin' in short_lower:
            self.discovered_patterns['mixin'] += 1
            return ('Utility', 75.0)
        
        # 26. Callback/Hook/Event patterns
        if any(x in short_lower for x in ['callback', 'hook', 'event', 'signal', 'listener', 'trigger']):
            self.discovered_patterns['callback'] += 1
            return ('EventHandler', 75.0)
        
        # 27. Patch/Mock/Stub (test doubles)
        if any(x in short_lower for x in ['patch', 'mock', 'stub', 'spy', 'double']):
            self.discovered_patterns['test_double'] += 1
            return ('Test', 75.0)
        
        # 28. Filter/Sort/Order patterns
        if any(x in short_lower for x in ['filter', 'sort', 'order', 'group', 'partition', 'bucket']):
            self.discovered_patterns['filter'] += 1
            return ('Query', 75.0)
        
        # 29. Config/Setting/Option patterns
        if any(x in short_lower for x in ['config', 'setting', 'option', 'preference', 'env', 'environ']):
            self.discovered_patterns['config'] += 1
            return ('Configuration', 75.0)
        
        # 30. Pool/Cache/Buffer patterns
        if any(x in short_lower for x in ['pool', 'cache', 'buffer', 'queue', 'stack']):
            self.discovered_patterns['cache'] += 1
            return ('Service', 75.0)
        
        # 31. Auth/Permission/Access patterns
        if any(x in short_lower for x in ['auth', 'permission', 'access', 'grant', 'deny', 'role', 'acl']):
            self.discovered_patterns['auth'] += 1
            return ('Policy', 75.0)
        
        # 32. Log/Trace/Debug patterns
        if any(x in short_lower for x in ['log', 'trace', 'debug', 'audit', 'metric', 'stat']):
            self.discovered_patterns['logging'] += 1
            return ('Utility', 75.0)
        
        # 33. Template/Render patterns
        if any(x in short_lower for x in ['template', 'render', 'generate', 'emit', 'produce']):
            self.discovered_patterns['template'] += 1
            return ('Factory', 75.0)
        
        # 34. Import/Export patterns
        if any(x in short_lower for x in ['import', 'export', 'ingest', 'extract', 'download', 'upload']):
            self.discovered_patterns['importexport'] += 1
            return ('Service', 75.0)
        
        # 35. Iterator/Generator patterns
        if any(x in short_lower for x in ['iter', 'generator', 'yield', 'stream', 'cursor', 'scroll']):
            self.discovered_patterns['iterator'] += 1
            return ('Iterator', 75.0)
        
        # 36. Clone/Copy/Duplicate patterns
        if any(x in short_lower for x in ['clone', 'copy', 'duplicate', 'replicate', 'mirror']):
            self.discovered_patterns['clone'] += 1
            return ('Factory', 75.0)
        
        # 37. Connect/Disconnect/Open/Close patterns
        if any(x in short_lower for x in ['connect', 'disconnect', 'open', 'close', 'start', 'stop', 'shutdown', 'terminate']):
            self.discovered_patterns['lifecycle'] += 1
            return ('Lifecycle', 75.0)
        
        # 38. Wrapper/Decorator patterns
        if any(x in short_lower for x in ['wrapper', 'decorator', 'wrap', 'decorate', 'proxy']):
            self.discovered_patterns['wrapper'] += 1
            return ('Utility', 75.0)
        
        # 39. Nested function patterns (common)
        if any(x in short_lower for x in ['inner', 'outer', 'closure', 'nested', 'wrapped']):
            self.discovered_patterns['nested'] += 1
            return ('Internal', 70.0)
        
        # 40. Count/Size/Length patterns
        if any(x in short_lower for x in ['count', 'size', 'length', 'total', 'sum', 'avg', 'min', 'max']):
            self.discovered_patterns['aggregate'] += 1
            return ('Query', 75.0)
        
        # 41. Compare/Diff/Match patterns  
        if any(x in short_lower for x in ['compare', 'diff', 'match', 'equal', 'same', 'similar']):
            self.discovered_patterns['compare'] += 1
            return ('Specification', 75.0)
        
        # 42. Split/Join/Concat patterns
        if any(x in short_lower for x in ['split', 'join', 'concat', 'append', 'prepend', 'extend']):
            self.discovered_patterns['string_ops'] += 1
            return ('Utility', 75.0)
        
        # 43. Wait/Sleep/Delay patterns
        if any(x in short_lower for x in ['wait', 'sleep', 'delay', 'timeout', 'pause', 'retry']):
            self.discovered_patterns['timing'] += 1
            return ('Utility', 75.0)
        
        # 44. Lock/Mutex/Semaphore patterns
        if any(x in short_lower for x in ['lock', 'mutex', 'semaphore', 'acquire', 'release', 'synchron']):
            self.discovered_patterns['concurrency'] += 1
            return ('Service', 75.0)
        
        # 45. Schedule/Job/Task/Worker patterns
        if any(x in short_lower for x in ['schedule', 'job', 'task', 'worker', 'cron', 'periodic', 'interval']):
            self.discovered_patterns['scheduler'] += 1
            return ('Job', 75.0)
        
        # 46. Parse/Lex/Token patterns
        if any(x in short_lower for x in ['parse', 'lex', 'token', 'ast', 'syntax', 'grammar']):
            self.discovered_patterns['parser'] += 1
            return ('Utility', 75.0)
        
        # 47. Format/Pretty/Style patterns
        if any(x in short_lower for x in ['format', 'pretty', 'style', 'beautify', 'minify', 'compress']):
            self.discovered_patterns['format'] += 1
            return ('Utility', 75.0)
        
        # 48. Version/Revision/History patterns
        if any(x in short_lower for x in ['version', 'revision', 'history', 'changelog', 'release']):
            self.discovered_patterns['version'] += 1
            return ('Query', 70.0)
        
        # 49. Short names (1-3 chars) are typically variables/lambdas - classify as Utility
        if len(short_lower) <= 3:
            self.discovered_patterns['short_name'] += 1
            return ('Utility', 60.0)
        
        # 50. CamelCase class names (starts uppercase) - check for patterns
        if short[0].isupper():
            # Classes with specific patterns
            if any(x in short_lower for x in ['exception', 'error']):
                return ('Exception', 75.0)
            if any(x in short_lower for x in ['factory', 'builder', 'creator']):
                return ('Factory', 75.0)
            if any(x in short_lower for x in ['handler', 'processor', 'worker']):
                return ('Service', 75.0)
            if any(x in short_lower for x in ['validator', 'checker', 'verifier']):
                return ('Validator', 75.0)
            if any(x in short_lower for x in ['service', 'manager', 'controller']):
                return ('Service', 75.0)
            if any(x in short_lower for x in ['repository', 'store', 'dao']):
                return ('Repository', 75.0)
            if any(x in short_lower for x in ['client', 'adapter', 'gateway']):
                return ('Adapter', 75.0)
            if any(x in short_lower for x in ['config', 'settings', 'options']):
                return ('Configuration', 75.0)
            # Generic class - likely DTO/Entity
            self.discovered_patterns['noun_entity'] += 1
            return ('DTO', 65.0)
        
        # 51. All remaining functions - classify by structure
        # If has underscores, likely internal utility
        if '_' in short_lower:
            self.discovered_patterns['underscore_func'] += 1
            return ('Utility', 60.0)
        
        # 52. camelCase functions (no underscore, starts lowercase)
        if short[0].islower() and '_' not in short:
            self.discovered_patterns['camelCase'] += 1
            return ('Utility', 60.0)
        
        # 53. Record as unknown for pattern analysis (should rarely reach here now)
        self.unknown_names.append(short_lower)
        return ('Unknown', 30.0)
    
    def get_pattern_report(self) -> Dict:
        """Generate report of discovered patterns."""
        # Analyze remaining unknown names for new patterns
        token_freq = Counter()
        for name in self.unknown_names:
            tokens = re.findall(r'[a-z]+', name)
            for token in tokens:
                if len(token) > 2:
                    token_freq[token] += 1
        
        return {
            'total_classified': sum(self.discovered_patterns.values()),
            'total_unknown': len(self.unknown_names),
            'top_patterns': self.discovered_patterns.most_common(20),
            'suggested_new_patterns': token_freq.most_common(10),
            'coverage': sum(self.discovered_patterns.values()) / 
                       (sum(self.discovered_patterns.values()) + len(self.unknown_names)) * 100
                       if (sum(self.discovered_patterns.values()) + len(self.unknown_names)) > 0 else 0
        }


def apply_heuristics(particles: List[Dict]) -> List[Dict]:
    """
    Apply heuristic classification to particles during pipeline.
    Modifies particles in place to update Unknown types.
    """
    discovery = HeuristicClassifier()
    updated = 0
    
    for particle in particles:
        if particle.get('type') == 'Unknown':
            name = particle.get('name', '')
            new_type, confidence = discovery.classify_by_pattern(name)
            
            if new_type != 'Unknown':
                particle['type'] = new_type
                particle['confidence'] = confidence
                particle['discovery_method'] = 'heuristic_pattern'
                updated += 1
    
    # Generate report
    report = discovery.get_pattern_report()
    report['particles_updated'] = updated
    
    return particles, report


if __name__ == '__main__':
    # Test
    test_names = [
        'test_user_login',
        'get_user_by_id',
        '__init__',
        '_private_method',
        'UserFactory',
        'handle_request',
        'some_random_function',
    ]
    
    discovery = HeuristicClassifier()
    for name in test_names:
        role, conf = discovery.classify_by_pattern(name)
        print(f'{name} -> {role} ({conf}%)')
    
    print()
    print('Report:', discovery.get_pattern_report())
