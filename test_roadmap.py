import sys
sys.path.append('.')
import scripts.generate_roadmap as gr

# mock mkdocs_gen_files
class MockGenFiles:
    def open(self, path, mode):
        return open('/tmp/test_roadmap.md', mode)
gr.mkdocs_gen_files = MockGenFiles()

gr.generate_roadmap()
print("Success")
