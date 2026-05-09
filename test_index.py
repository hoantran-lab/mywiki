import sys
sys.path.append('.')
import scripts.generate_index as gi

class MockGenFiles:
    def open(self, path, mode):
        return open('/tmp/test_index.md', mode, encoding='utf-8')
gi.mkdocs_gen_files = MockGenFiles()

gi.generate_index()
