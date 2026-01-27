#!/usr/bin/env python3
"""Aggressive paper finder using Semantic Scholar API with exact queries."""

import json
import os
import time
import urllib.request
import urllib.parse
import ssl

REFS_DIR = os.path.dirname(os.path.abspath(__file__))

PAPERS = [
    ("REF-003", "Lambek", "1980", "Lambda Calculus Cartesian Closed Categories", [
        "https://www.math.mcgill.ca/barr/lambek/pdffiles/FromlacalctoCCC.pdf",
        "https://link.springer.com/content/pdf/10.1007/978-3-642-67828-1_18.pdf",
    ]),
    ("REF-013", "Poincare", "1895", "Analysis Situs", [
        "https://www.maths.ed.ac.uk/~v1ranick/papers/poincare2009.pdf",
    ]),
    ("REF-014", "Euler", "1736", "Seven Bridges Konigsberg", [
        "https://www.maa.org/sites/default/files/pdf/upload_library/22/Polya/07468342.di020723.02p0016r.pdf",
    ]),
    ("REF-021", "Wille", "1982", "Restructuring Lattice Theory", []),
    ("REF-026", "Kolmogorov", "1965", "Three Approaches Information", [
        "https://www.mathnet.ru/links/b6e6c3d7b12c2a2cae58cc5798aa3bf6/ppi1029.pdf",
        "https://link.springer.com/content/pdf/10.1007/BF02392379.pdf",
    ]),
    ("REF-028", "Bejan", "1997", "Constructal Theory Conducting Paths", []),
    ("REF-031", "Onsager", "1931", "Reciprocal Relations Irreversible", [
        "https://web.archive.org/web/20201/https://faculty.washington.edu/ghMDRtm/Handouts/Onsager1.pdf",
    ]),
    ("REF-035", "Weinberg", "1979", "Phenomenological Lagrangians", []),
    ("REF-036", "Nambu", "1960", "Quasi-particles Gauge Superconductivity", []),
    ("REF-037", "Yang", "1954", "Isotopic Spin Gauge Invariance", []),
    ("REF-045", "Peirce", "1903", "Categories Defended", []),
    ("REF-047", "Lotman", "1984", "Semiosphere", [
        "https://www.ut.ee/SOSE/sss/pdf/lotman14.pdf",
    ]),
    ("REF-050", "Atkin", "2006", "Peirce Theory Signs SEP", []),  # HTML only
    ("REF-051", "Tarski", "1933", "Concept Truth Formalized Languages", [
        "https://web.archive.org/web/2024/https://www.hist-analytic.com/Tarski.pdf",
    ]),
    ("REF-056", "Ladyman", "1998", "Structural Realism", [
        "https://www.bristol.ac.uk/media-library/sites/philosophy/documents/what-is-structural-realism.pdf",
    ]),
    ("REF-058", "Williams", "1953", "Elements Being", []),
    ("REF-061", "French", "2011", "Ontic Structural Realism", [
        "https://eprints.whiterose.ac.uk/3467/1/InDefence.pdf",
    ]),
    ("REF-064", "Davidson", "1963", "Actions Reasons Causes", [
        "https://andrewmbailey.com/dfc/Davidson_Actions.pdf",
        "https://www.ucs.mun.ca/~alwood/davidson_rac.pdf",
    ]),
    ("REF-075", "Clarke", "1986", "Automatic Verification Finite State", [
        "https://www.cs.cmu.edu/~emc/15-820A/reading/CES_86.pdf",
    ]),
    ("REF-076", "Manna", "1980", "Deductive Program Synthesis", [
        "https://apps.dtic.mil/sti/pdfs/ADA087398.pdf",
        "https://www.cs.utexas.edu/~moore/acl2/seminar/manna-waldinger-1980.pdf",
    ]),
    ("REF-077", "Back", "1988", "Calculus Refinements", [
        "https://link.springer.com/content/pdf/10.1007/BF00264457.pdf",
    ]),
    ("REF-085", "Langton", "1990", "Computation Edge Chaos", [
        "https://www.cs.unibo.it/~roli/AL/Papers/langton_EOC.pdf",
    ]),
    ("REF-091", "Gibson", "1977", "Theory Affordances", [
        "https://monoskop.org/images/4/4c/Gibson_James_J_1977_The_Theory_of_Affordances.pdf",
        "https://cs.brown.edu/courses/cs137/readings/Gibson-AFF.pdf",
    ]),
    ("REF-096", "Sweller", "1988", "Cognitive Load Problem Solving", []),
    ("REF-104", "Wilson", "2007", "Rethinking Sociobiology", [
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2654773/pdf/nihms-88147.pdf",
    ]),
    ("REF-110", "Arthur", "1989", "Competing Technologies Lock-In", [
        "https://dimetic.dime-eu.org/dimetic_files/arthurej1989.pdf",
    ]),
    ("REF-113", "Myerson", "1981", "Optimal Auction Design", [
        "https://dspace.mit.edu/bitstream/handle/1721.1/64048/optimalauctionde00myer.pdf",
    ]),
    ("REF-115", "Krogstie", "2006", "Process Models Knowledge Action", []),
    ("REF-117", "Hjorland", "2008", "Knowledge Organization KO", []),
    ("REF-120", "Stiny", "1980", "Shape Grammars", []),
    ("REF-124", "Lyapunov", "1892", "Stability Motion", [
        "https://www.math.u-szeged.hu/ejqtde/Lyapunov.pdf",
    ]),
    ("REF-125", "Montague", "1970", "Universal Grammar", []),
]


def ss_search(query, limit=5):
    """Search Semantic Scholar for open access PDF."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = urllib.parse.urlencode({
        "query": query,
        "limit": limit,
        "fields": "title,year,openAccessPdf,externalIds"
    })
    ctx = ssl.create_default_context()
    req = urllib.request.Request(f"{url}?{params}", headers={"User-Agent": "SMoC-RefLib/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            for paper in data.get("data", []):
                oa = paper.get("openAccessPdf")
                if oa and oa.get("url"):
                    return oa["url"], paper.get("title", "")
    except Exception:
        pass
    return None, None


def download_pdf(url, filepath):
    """Download and verify PDF."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=45, context=ctx) as resp:
            data = resp.read()
            if b"%PDF" in data[:1024] and len(data) > 5000:
                with open(filepath, "wb") as f:
                    f.write(data)
                return True, len(data)
    except Exception:
        pass
    return False, 0


def main():
    print(f"Searching for {len(PAPERS)} missing papers...")
    print()

    downloaded = 0
    already = 0

    for ref_id, author, year, short_title, urls in PAPERS:
        # Build filename
        clean_title = short_title.replace(" ", "")[:30]
        filename = f"{ref_id}_{author}_{year}_{clean_title}.pdf"
        filepath = os.path.join(REFS_DIR, filename)

        # Skip if exists
        existing = [f for f in os.listdir(REFS_DIR) if f.startswith(ref_id) and f.endswith(".pdf")]
        if existing:
            print(f"  HAVE {ref_id} ({existing[0]})")
            already += 1
            continue

        print(f"  FIND {ref_id}: {author} ({year}) - {short_title}")

        got = False

        # Try curated URLs first
        for url in urls:
            if "archive.org/download" in url or "jstor.org/stable" in url:
                continue  # skip known failures
            ok, sz = download_pdf(url, filepath)
            if ok:
                print(f"       DIRECT -> {filename} ({sz:,} bytes)")
                downloaded += 1
                got = True
                break

        if got:
            continue

        # Try Semantic Scholar
        query = f"{author} {year} {short_title}"
        ss_url, ss_title = ss_search(query)
        if ss_url:
            ok, sz = download_pdf(ss_url, filepath)
            if ok:
                print(f"       SS [{ss_title[:40]}...] -> {filename} ({sz:,} bytes)")
                downloaded += 1
                got = True

        if not got:
            # Try broader SS search
            query2 = f"{short_title} {author}"
            ss_url2, ss_title2 = ss_search(query2)
            if ss_url2 and ss_url2 != ss_url:
                ok, sz = download_pdf(ss_url2, filepath)
                if ok:
                    print(f"       SS2 [{ss_title2[:40]}...] -> {filename} ({sz:,} bytes)")
                    downloaded += 1
                    got = True

        if not got:
            print(f"       MISS")

        time.sleep(0.8)  # rate limit

    print()
    print(f"=== RESULTS ===")
    print(f"Already had: {already}")
    print(f"New downloads: {downloaded}")
    print(f"Total PDFs: {len([f for f in os.listdir(REFS_DIR) if f.endswith('.pdf')])}")


if __name__ == "__main__":
    main()
