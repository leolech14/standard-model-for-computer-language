#!/usr/bin/env python3
"""Search Semantic Scholar + known URLs for remaining references."""

import json
import os
import time
import urllib.request
import urllib.parse
import urllib.error
import ssl

REFS_DIR = os.path.dirname(os.path.abspath(__file__))

# All 89 missing references with search queries and known alternate URLs
MISSING = {
    "REF-003": {
        "query": "Lambek 1980 Lambda Calculus Cartesian Closed Categories",
        "urls": []
    },
    "REF-007": {
        "query": "Mac Lane 1971 Categories Working Mathematician",
        "urls": []  # book, unlikely free
    },
    "REF-008": {
        "query": "Awodey 2010 Category Theory",
        "urls": ["https://www.andrew.cmu.edu/course/80-413-713/notes/"]  # might have notes
    },
    "REF-012": {
        "query": "Freeman Pfenning 1991 Refinement Types ML",
        "urls": ["https://www.cs.cmu.edu/~fp/papers/pldi91.pdf"]
    },
    "REF-013": {
        "query": "Poincare 1895 Analysis Situs",
        "urls": []  # historical, French
    },
    "REF-014": {
        "query": "Euler 1736 Seven Bridges Konigsberg",
        "urls": ["https://archive.org/download/commentaborealiq06teleod/commentaborealiq06teleod.pdf"]
    },
    "REF-015": {
        "query": "Carlsson 2009 Topology Data Bulletin AMS",
        "urls": ["https://www.ams.org/journals/bull/2009-46-02/S0273-0979-09-01249-X/S0273-0979-09-01249-X.pdf"]
    },
    "REF-016": {
        "query": "Singh Memoli Carlsson 2007 Topological Methods High Dimensional Data",
        "urls": ["https://research.math.osu.edu/tgda/mapperPBG.pdf"]
    },
    "REF-017": {
        "query": "Chung 1997 Spectral Graph Theory",
        "urls": ["https://mathweb.ucsd.edu/~fan/research/revised.html"]
    },
    "REF-019": {
        "query": "Edelsbrunner Harer 2010 Computational Topology",
        "urls": []  # book
    },
    "REF-020": {
        "query": "Ghrist 2014 Elementary Applied Topology",
        "urls": ["https://www2.math.upenn.edu/~ghrist/EAT/EAT.pdf"]
    },
    "REF-021": {
        "query": "Wille 1982 Restructuring Lattice Theory",
        "urls": []
    },
    "REF-024": {
        "query": "Ganter Wille 1999 Formal Concept Analysis",
        "urls": []  # book
    },
    "REF-026": {
        "query": "Kolmogorov 1965 Three Approaches Quantitative Definition Information",
        "urls": ["https://alexander.shen.free.fr/library/Kolmogorov65_Three-Approaches-to-Information.pdf"]
    },
    "REF-027": {
        "query": "Amari 1985 Differential Geometrical Methods Statistics",
        "urls": []  # book
    },
    "REF-028": {
        "query": "Bejan 1997 Constructal theory network conducting paths",
        "urls": []
    },
    "REF-031": {
        "query": "Onsager 1931 Reciprocal Relations Irreversible Processes",
        "urls": ["https://web.archive.org/web/20200217094655/https://faculty.washington.edu/ghMDRtm/Handouts/Onsager1.pdf"]
    },
    "REF-032": {
        "query": "Bejan Zane 2012 Design in Nature",
        "urls": []  # book
    },
    "REF-033": {
        "query": "Kondepudi Prigogine 2014 Modern Thermodynamics",
        "urls": []  # book
    },
    "REF-034": {
        "query": "Wilson 1971 Renormalization Group Critical Phenomena",
        "urls": ["https://journals.aps.org/prb/abstract/10.1103/PhysRevB.4.3174"]
    },
    "REF-035": {
        "query": "Weinberg 1979 Phenomenological Lagrangians Physica",
        "urls": []
    },
    "REF-036": {
        "query": "Nambu 1960 Quasi-particles Gauge Invariance Superconductivity",
        "urls": []
    },
    "REF-037": {
        "query": "Yang Mills 1954 Conservation Isotopic Spin Gauge Invariance",
        "urls": ["https://journals.aps.org/pr/abstract/10.1103/PhysRev.96.191"]
    },
    "REF-038": {
        "query": "Cardy 1996 Scaling Renormalization Statistical Physics",
        "urls": []  # book
    },
    "REF-041": {
        "query": "Friston 2017 Active Inference Learning",
        "urls": []
    },
    "REF-042": {
        "query": "Pearl 1988 Probabilistic Reasoning Intelligent Systems",
        "urls": []  # book
    },
    "REF-043": {
        "query": "Parr Pezzulo Friston 2022 Active Inference Free Energy",
        "urls": []  # book
    },
    "REF-044": {
        "query": "Peirce Collected Papers semiotics",
        "urls": []  # book, 8 vols
    },
    "REF-045": {
        "query": "Peirce 1903 Categories Defended",
        "urls": []
    },
    "REF-046": {
        "query": "Morris 1938 Foundations Theory Signs",
        "urls": ["https://archive.org/details/foundationsofthe0000morr"]
    },
    "REF-047": {
        "query": "Lotman 1984 On the Semiosphere Sign Systems Studies",
        "urls": ["https://www.ut.ee/SOSE/sss/pdf/Lotman_2005_1.pdf"]
    },
    "REF-048": {
        "query": "Eco 1976 Theory Semiotics",
        "urls": []  # book
    },
    "REF-049": {
        "query": "Deely 1990 Basics Semiotics",
        "urls": []  # book
    },
    "REF-050": {
        "query": "Atkin Peirce Theory Signs Stanford Encyclopedia Philosophy",
        "urls": ["https://plato.stanford.edu/entries/peirce-semiotics/"]
    },
    "REF-051": {
        "query": "Tarski 1933 Concept Truth Formalized Languages",
        "urls": ["https://www.hist-analytic.com/Tarski.pdf"]
    },
    "REF-054": {
        "query": "Hodges 1997 Shorter Model Theory",
        "urls": []  # book
    },
    "REF-055": {
        "query": "Whitehead 1929 Process Reality",
        "urls": ["https://archive.org/details/processrealitygi00alfr"]  # IA borrow
    },
    "REF-056": {
        "query": "Ladyman 1998 What is Structural Realism Synthese",
        "urls": ["https://www.jstor.org/stable/20117397"]
    },
    "REF-057": {
        "query": "Bhaskar 1975 Realist Theory Science",
        "urls": []  # book
    },
    "REF-058": {
        "query": "Williams 1953 On Elements Being",
        "urls": []
    },
    "REF-059": {
        "query": "Frege 1892 Uber Sinn und Bedeutung Sense Reference",
        "urls": [
            "https://www.jstor.org/stable/40093833",
            "http://www.scu.edu.tw/philos/98class/Peng/05.pdf"
        ]
    },
    "REF-060": {
        "query": "Rescher 2000 Process Philosophy Survey Basic Issues",
        "urls": []  # book
    },
    "REF-061": {
        "query": "French Ladyman 2011 Defence Ontic Structural Realism",
        "urls": []
    },
    "REF-062": {
        "query": "Dennett 1987 Intentional Stance",
        "urls": []  # book
    },
    "REF-064": {
        "query": "Davidson 1963 Actions Reasons Causes Journal Philosophy",
        "urls": ["https://www.jstor.org/stable/2023177"]
    },
    "REF-065": {
        "query": "Bratman 1999 Faces Intention",
        "urls": []  # book
    },
    "REF-066": {
        "query": "Robert Martin 2012 Clean Architecture",
        "urls": []  # book, commercial
    },
    "REF-067": {
        "query": "Eric Evans 2003 Domain Driven Design",
        "urls": []  # book, commercial
    },
    "REF-068": {
        "query": "Gamma Helm Johnson Vlissides 1994 Design Patterns",
        "urls": []  # book, commercial
    },
    "REF-070": {
        "query": "Christopher Alexander 2002 Nature Order",
        "urls": []  # book, 4 vols
    },
    "REF-071": {
        "query": "Halstead 1977 Elements Software Science",
        "urls": []  # book
    },
    "REF-075": {
        "query": "Clarke Emerson Sistla 1986 Automatic Verification Finite State Concurrent",
        "urls": []
    },
    "REF-076": {
        "query": "Manna Waldinger 1980 Deductive Approach Program Synthesis",
        "urls": ["https://www.cs.utexas.edu/~moore/acl2/seminar/manna-waldinger-1980.pdf"]
    },
    "REF-077": {
        "query": "Back 1988 Calculus Refinements Program Derivations",
        "urls": []
    },
    "REF-078": {
        "query": "Koestler 1967 Ghost in the Machine",
        "urls": ["https://archive.org/details/ghostinmachine0000koes"]  # IA borrow
    },
    "REF-079": {
        "query": "Beer 1972 Brain of the Firm",
        "urls": []  # book
    },
    "REF-082": {
        "query": "Holland 1998 Emergence Chaos Order",
        "urls": []  # book
    },
    "REF-085": {
        "query": "Langton 1990 Computation Edge Chaos",
        "urls": ["https://sfi-edu.s3.amazonaws.com/sfi-edu/production/uploads/sfi-com/dev/uploads/filer/bf/bf6a9252-47b0-41be-9b8b-1a0e434c0bc8/90-007.pdf"]
    },
    "REF-089": {
        "query": "Lakoff Johnson 1980 Metaphors We Live By",
        "urls": []  # book
    },
    "REF-091": {
        "query": "Gibson 1977 Theory Affordances Perceiving Acting Knowing",
        "urls": ["https://cs.brown.edu/courses/cs137/readings/Gibson-AFF.pdf"]
    },
    "REF-092": {
        "query": "Suchman 1987 Plans Situated Actions",
        "urls": []  # book
    },
    "REF-093": {
        "query": "Hutchins 1995 Cognition in Wild",
        "urls": []  # book
    },
    "REF-096": {
        "query": "Sweller 1988 Cognitive Load Problem Solving",
        "urls": ["https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog1202_4"]
    },
    "REF-099": {
        "query": "Waddington 1957 Strategy Genes",
        "urls": []  # book
    },
    "REF-100": {
        "query": "Oyama 1985 Ontogeny Information",
        "urls": []  # book
    },
    "REF-101": {
        "query": "Maturana Varela 1980 Autopoiesis Cognition",
        "urls": []  # book
    },
    "REF-102": {
        "query": "Varela Thompson Rosch 1991 Embodied Mind",
        "urls": []  # book
    },
    "REF-103": {
        "query": "Rosen 1991 Life Itself",
        "urls": []  # book
    },
    "REF-104": {
        "query": "Wilson Wilson 2007 Rethinking Theoretical Foundation Sociobiology",
        "urls": []
    },
    "REF-105": {
        "query": "Odling-Smee 2003 Niche Construction",
        "urls": []  # book
    },
    "REF-106": {
        "query": "Carroll 2005 Endless Forms Most Beautiful",
        "urls": []  # book
    },
    "REF-107": {
        "query": "Latour 2005 Reassembling Social",
        "urls": []  # book
    },
    "REF-108": {
        "query": "Giddens 1984 Constitution Society",
        "urls": []  # book
    },
    "REF-109": {
        "query": "Bijker 1995 Bicycles Bakelites Bulbs",
        "urls": []  # book
    },
    "REF-110": {
        "query": "Arthur 1989 Competing Technologies Increasing Returns Lock-In",
        "urls": ["https://www.jstor.org/stable/2234208"]
    },
    "REF-111": {
        "query": "Nelson Winter 1982 Evolutionary Theory Economic Change",
        "urls": []  # book
    },
    "REF-112": {
        "query": "Williamson 1985 Economic Institutions Capitalism",
        "urls": []  # book
    },
    "REF-113": {
        "query": "Myerson 1981 Optimal Auction Design Mathematics Operations Research",
        "urls": ["https://pubsonline.informs.org/doi/abs/10.1287/moor.6.1.58"]
    },
    "REF-114": {
        "query": "Ranganathan 1933 Colon Classification",
        "urls": ["https://archive.org/details/colonclassificat0000rang"]  # IA
    },
    "REF-115": {
        "query": "Krogstie 2006 Process models representing knowledge action",
        "urls": []
    },
    "REF-116": {
        "query": "Wilkinson 1999 Grammar Graphics",
        "urls": []  # book
    },
    "REF-117": {
        "query": "Hjorland 2008 What Knowledge Organization KO",
        "urls": []
    },
    "REF-118": {
        "query": "Alexander 1977 Pattern Language",
        "urls": []  # book
    },
    "REF-119": {
        "query": "Simon 1969 Sciences Artificial",
        "urls": ["https://monoskop.org/images/9/9c/Simon_Herbert_A_The_Sciences_of_the_Artificial_3rd_ed.pdf"]
    },
    "REF-120": {
        "query": "Stiny 1980 Introduction Shape Shape Grammars",
        "urls": []
    },
    "REF-122": {
        "query": "Kalman 1960 New Approach Linear Filtering Prediction",
        "urls": ["https://www.cs.unc.edu/~welch/kalman/media/pdf/Kalman1960.pdf"]
    },
    "REF-123": {
        "query": "Wiener 1948 Cybernetics Control Communication",
        "urls": ["https://archive.org/details/cybaborcommuininani0000wiene"]  # IA
    },
    "REF-124": {
        "query": "Lyapunov 1892 General Problem Stability Motion",
        "urls": ["https://www.math.u-szeged.hu/ejqtde/Lyapunov.pdf"]
    },
    "REF-125": {
        "query": "Montague 1970 Universal Grammar Theoria",
        "urls": []
    },
}


def search_semantic_scholar(query):
    """Search Semantic Scholar for open access PDF."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = urllib.parse.urlencode({
        "query": query,
        "limit": 3,
        "fields": "title,year,openAccessPdf,externalIds,url"
    })
    full_url = f"{url}?{params}"

    ctx = ssl.create_default_context()
    req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            for paper in data.get("data", []):
                oa = paper.get("openAccessPdf")
                if oa and oa.get("url"):
                    return oa["url"], paper.get("title", "")
    except Exception as e:
        pass
    return None, None


def download_pdf(url, filepath):
    """Download PDF and verify it's valid."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    })
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = resp.read()
            if data[:5] == b"%PDF-" or b"%PDF" in data[:1024]:
                with open(filepath, "wb") as f:
                    f.write(data)
                return True, len(data)
    except Exception:
        pass
    return False, 0


def main():
    os.makedirs(REFS_DIR, exist_ok=True)

    print(f"Searching for {len(MISSING)} missing references...")
    print()

    found = 0
    downloaded = 0
    books_skipped = 0

    for ref_id, info in sorted(MISSING.items()):
        query = info["query"]
        urls = info["urls"]

        # Skip if already downloaded
        existing = [f for f in os.listdir(REFS_DIR) if f.startswith(ref_id) and f.endswith(".pdf")]
        if existing:
            print(f"  SKIP {ref_id} (already have {existing[0]})")
            continue

        print(f"  SEARCH {ref_id}: {query[:60]}...")

        # Try known URLs first
        pdf_url = None
        for url in urls:
            if url.endswith(".pdf"):
                pdf_url = url
                break

        # Then try Semantic Scholar
        if not pdf_url:
            ss_url, ss_title = search_semantic_scholar(query)
            if ss_url:
                pdf_url = ss_url
                print(f"         SS found: {ss_title[:50]}...")
            time.sleep(0.5)  # rate limit

        if pdf_url:
            found += 1
            # Build filename
            parts = query.split()
            author = parts[0] if parts else "Unknown"
            year = ""
            for p in parts:
                if p.isdigit() and len(p) == 4:
                    year = p
                    break
            short_title = "".join(p.title() for p in parts[2:5] if not p.isdigit())
            filename = f"{ref_id}_{author}_{year}_{short_title}.pdf"
            filepath = os.path.join(REFS_DIR, filename)

            ok, size = download_pdf(pdf_url, filepath)
            if ok:
                print(f"         OK -> {filename} ({size:,} bytes)")
                downloaded += 1
            else:
                print(f"         FAIL download")
        else:
            print(f"         -- no free source found")

    print()
    print(f"=== RESULTS ===")
    print(f"Searched:    {len(MISSING)}")
    print(f"URLs found:  {found}")
    print(f"Downloaded:  {downloaded}")
    print(f"Total PDFs:  {len([f for f in os.listdir(REFS_DIR) if f.endswith('.pdf')])}")


if __name__ == "__main__":
    main()
