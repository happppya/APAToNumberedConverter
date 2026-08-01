import re
import os

class CitationConverter:
    def __init__(self, manual_mapping=None):
        self.citation_map = {}
        self.current_index = 1
        self.original_bibliography = []
        self.manual_mapping = manual_mapping or {}
        
        self.master_re = re.compile(
            r'(?P<parenthetical>\(\s*(?:[^,();]+,\s*\d{4}[a-z]?\s*;\s*)*[^,();]+,\s*\d{4}[a-z]?\s*\))|'
            r'(?P<narrative>(?P<n_auth>[a-zA-Z\-\s&,]+?(?:\s+et\s+al\.)?)\s+\((?P<n_year>\d{4}[a-z]?)\))'
        )

    def _normalize_author_key(self, author_str):
        s = author_str.strip()
        s = s.replace(" and ", " & ")
        
        if "et al." in s:
            prefix = s.split("et al.")[0].strip()
            last_word = prefix.split()[-1].rstrip(',')
            return f"{last_word} et al."
        elif "&" in s:
            parts = s.split("&")
            auth1 = parts[0].strip().split()[-1].rstrip(',') if parts[0].strip().split() else ""
            auth2 = parts[1].strip().split()[0].rstrip(',') if parts[1].strip().split() else ""
            return f"{auth1} & {auth2}"
        else:
            return s.split()[-1].rstrip(',')

    def get_citation_number(self, author, year):
        author_key = self._normalize_author_key(author)
        
        # Apply manual mapping early to unify citation numbers
        if author_key in self.manual_mapping:
            author_key = self.manual_mapping[author_key]
        else:
            # Fallback if mapping excludes et al
            primary_author = author_key.replace(" et al.", "").split("&")[0].strip()
            if primary_author in self.manual_mapping:
                if "et al." in author_key:
                    author_key = f"{self.manual_mapping[primary_author]} et al."
                elif "&" in author_key:
                    second_author = author_key.split("&")[1].strip()
                    author_key = f"{self.manual_mapping[primary_author]} & {second_author}"
                else:
                    author_key = self.manual_mapping[primary_author]

        year_key = year.strip()
        key = (author_key, year_key)
        
        if key not in self.citation_map:
            self.citation_map[key] = self.current_index
            self.current_index += 1
            
        return self.citation_map[key]

    def _replace_master(self, match):
        if match.group('parenthetical'):
            raw_content = match.group('parenthetical').strip('() \t')
            citations = raw_content.split(';')
            nums = []
            
            for cit in citations:
                parts = cit.split(',')
                if len(parts) >= 2:
                    auth = ','.join(parts[:-1]).strip()
                    year = parts[-1].strip()
                    nums.append(str(self.get_citation_number(auth, year)))
                    
            return f"({', '.join(nums)})"
            
        elif match.group('narrative'):
            auth = match.group('n_auth')
            year = match.group('n_year')
            num = self.get_citation_number(auth, year)
            return f"{auth.rstrip()} ({num})"
        
        return match.group(0)

    def process_text(self, input_text):
        return self.master_re.sub(self._replace_master, input_text)

    def load_bibliography(self, filepath):
        if not os.path.exists(filepath):
            print(f"Warning: Bibliography file '{filepath}' not found.")
            return
        with open(filepath, 'r', encoding='utf-8') as f:
            self.original_bibliography = [line.strip() for line in f if line.strip()]

    def generate_new_bibliography(self):
        new_bib = []
        sorted_citations = sorted(self.citation_map.items(), key=lambda item: item[1])
        
        for (author, year), num in sorted_citations:
            matched_line = None
            
            search_author = author.replace(" et al.", "").split("&")[0].strip()
            
            for line in self.original_bibliography:
                if search_author in line and year in line:
                    matched_line = line
                    break
            
            if matched_line:
                new_bib.append(f"{num}. {matched_line}")
                # Safe to remove now, because duplicate citations were grouped into a single loop iteration
                self.original_bibliography.remove(matched_line) 
            else:
                new_bib.append(f"{num}. [MANUAL REVIEW REQUIRED] Could not automatically match: {author}, {year}")
                
        return "\n\n".join(new_bib)

def main():
    input_paper_path = "input_text.txt"
    input_bib_path = "input_bibliography.txt"
    output_paper_path = "output_paper.txt"
    output_bib_path = "output_bibliography.txt"

    # Add your manual overrides here
    author_overrides = {
        "s": "Barnes", # In this example, it maps the incorrectly recognized "s" to "Barnes". This was happening because my paper had "Barnes's"
        "nkel": "Sünkel" # In this example, it can't recognize the u with the dots for some reason
    }

    converter = CitationConverter(manual_mapping=author_overrides)
    converter.load_bibliography(input_bib_path)

    print("Reading input paper...")
    try:
        with open(input_paper_path, 'r', encoding='utf-8') as f:
            paper_text = f.read()
    except FileNotFoundError:
        print(f"Error: Please create '{input_paper_path}' in the same directory.")
        return

    print("Converting citations...")
    converted_text = converter.process_text(paper_text)

    with open(output_paper_path, 'w', encoding='utf-8') as f:
        f.write(converted_text)
    print(f"Success: Updated paper written to '{output_paper_path}'")

    print("Generating reordered bibliography...")
    new_bib_text = converter.generate_new_bibliography()
    with open(output_bib_path, 'w', encoding='utf-8') as f:
        f.write(new_bib_text)
    print(f"Success: Updated bibliography written to '{output_bib_path}'")

if __name__ == "__main__":
    main()