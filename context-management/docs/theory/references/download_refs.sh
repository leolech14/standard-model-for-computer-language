#!/bin/bash
# Download free references for the Standard Model of Code Reference Library
# Only downloads from known free/legal sources

DEST="/Users/lech/PROJECTS_all/PROJECT_elements/context-management/docs/theory/references"
cd "$DEST"

echo "=== SMoC Reference Library Downloader ==="
echo "Destination: $DEST"
echo ""

downloaded=0
failed=0
skipped=0

dl() {
    local id="$1"
    local url="$2"
    local filename="$3"

    if [ -f "$filename" ]; then
        echo "  SKIP $id - already exists"
        ((skipped++))
        return
    fi

    echo "  GET  $id -> $filename"
    if curl -sL --max-time 30 -o "$filename" "$url" 2>/dev/null; then
        # Check if we got an actual PDF (not an HTML error page)
        local ftype=$(file -b "$filename" | head -1)
        if echo "$ftype" | grep -qi "pdf"; then
            local size=$(wc -c < "$filename" | tr -d ' ')
            echo "       OK ($size bytes)"
            ((downloaded++))
        else
            echo "       FAIL (not a PDF: $ftype)"
            rm -f "$filename"
            ((failed++))
        fi
    else
        echo "       FAIL (download error)"
        rm -f "$filename"
        ((failed++))
    fi
}

echo "--- arXiv papers ---"
dl "REF-005" "https://arxiv.org/pdf/2404.04837" "REF-005_Patterson_2024_GATlab.pdf"
dl "REF-095" "https://arxiv.org/pdf/2307.03172" "REF-095_Liu_2023_LostInTheMiddle.pdf"

echo ""
echo "--- Classic papers (public domain / open access) ---"

# Shannon 1948 - Bell Labs, freely available
dl "REF-025" "https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf" "REF-025_Shannon_1948_MathematicalTheoryCommunication.pdf"

# Turing 1952 - Royal Society, open
dl "REF-098" "https://www.dna.caltech.edu/courses/cs191/paperscs191/turing.pdf" "REF-098_Turing_1952_ChemicalBasisMorphogenesis.pdf"

# Simon 1962 - Architecture of Complexity
dl "REF-081" "https://faculty.sites.iastate.edu/tesfatsi/archive/tesfatsi/ArchitectureOfComplexity.HSimon1962.pdf" "REF-081_Simon_1962_ArchitectureOfComplexity.pdf"

# Gödel 1931 - public domain
dl "REF-052" "https://monoskop.org/images/9/93/Godel_Kurt_1931_On_Formally_Undecidable_Propositions_of_Principia_Mathematica_and_Related_Systems_I.pdf" "REF-052_Godel_1931_FormallyUndecidable.pdf"

# Anderson 1972 - More Is Different
dl "REF-039" "https://cse-robotics.engr.tamu.edu/dshell/cs689/papers/anderson72more_is_different.pdf" "REF-039_Anderson_1972_MoreIsDifferent.pdf"

# Miller 1956 - Magical Number Seven
dl "REF-097" "http://www.musanim.com/miller1956.pdf" "REF-097_Miller_1956_MagicalNumberSeven.pdf"

# Dijkstra 1968 - THE multiprogramming system
dl "REF-069" "https://www.cs.utexas.edu/~EWD/ewd01xx/EWD196.PDF" "REF-069_Dijkstra_1968_THEMultiprogramming.pdf"

# Ashby 1956 - Introduction to Cybernetics (public domain)
dl "REF-080" "http://pespmc1.vub.ac.be/books/IntroCyb.pdf" "REF-080_Ashby_1956_IntroCybernetics.pdf"

# Jaynes 1957 - Information Theory and Statistical Mechanics
dl "REF-030" "https://bayes.wustl.edu/etj/articles/theory.1.pdf" "REF-030_Jaynes_1957_InfoTheoryStatMech.pdf"

# Prigogine 1977 - Nobel lecture
dl "REF-029" "https://www.nobelprize.org/uploads/2018/06/prigogine-lecture.pdf" "REF-029_Prigogine_1977_TimeStructureFluctuations.pdf"

# McCabe 1976 - Complexity Measure
dl "REF-072" "https://www.literateprogramming.com/mccabe.pdf" "REF-072_McCabe_1976_ComplexityMeasure.pdf"

# Lawvere 1969 - Diagonal arguments
dl "REF-001" "https://raw.githubusercontent.com/mattearnshaw/lawvere/master/pdfs/1969-diagonal-arguments-and-cartesian-closed-categories.pdf" "REF-001_Lawvere_1969_DiagonalArguments.pdf"

# Carlsson 2009 - Topology and Data
dl "REF-015" "https://www.ams.org/journals/bull/2009-46-02/S0273-0979-09-01249-X/S0273-0979-09-01249-X.pdf" "REF-015_Carlsson_2009_TopologyAndData.pdf"

# Hatcher 2002 - Algebraic Topology (author's free version)
dl "REF-018" "https://pi.math.cornell.edu/~hatcher/AT/AT.pdf" "REF-018_Hatcher_2002_AlgebraicTopology.pdf"

# Ghrist 2014 - Elementary Applied Topology (author's free version)
dl "REF-020" "https://www2.math.upenn.edu/~ghrist/notes.html" "SKIP_REF-020"
# Actually the full PDF:
dl "REF-020" "https://www2.math.upenn.edu/~ghrist/EAT/EAT.pdf" "REF-020_Ghrist_2014_ElementaryAppliedTopology.pdf"

# Abramsky & Jung 1994 - Domain Theory
dl "REF-023" "https://www.cs.bham.ac.uk/~axj/pub/papers/handy1.pdf" "REF-023_Abramsky_Jung_1994_DomainTheory.pdf"

# Friston 2010 - Free Energy Principle
dl "REF-040" "https://www.fil.ion.ucl.ac.uk/~karl/The%20free-energy%20principle%20-%20a%20unified%20brain%20theory.pdf" "REF-040_Friston_2010_FreeEnergyPrinciple.pdf"

# Tononi 2004 - IIT (BMC Neuroscience - open access)
dl "REF-086" "https://bmcneurosci.biomedcentral.com/counter/pdf/10.1186/1471-2202-5-42.pdf" "REF-086_Tononi_2004_InformationIntegration.pdf"

# Tononi 2016 - IIT (PLOS - open access)
dl "REF-087" "https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005078&type=printable" "REF-087_Tononi_2016_IIT.pdf"

# HoTT book - freely available
dl "REF-010" "https://homotopytypetheory.org/wp-content/uploads/2013/03/hott-online-1287-g1ac9408.pdf" "REF-010_UnivalentFoundations_2013_HoTT.pdf"

# Milewski - Category Theory for Programmers (free)
dl "REF-006" "https://github.com/hmemcpy/milern-category-theory-for-programmers/releases/download/v1.3.0/category-theory-for-programmers.pdf" "SKIP_REF-006"
# Try alternate URL
dl "REF-006" "https://bartoszmilewski.com/wp-content/uploads/2019/04/category-theory-for-programmers.pdf" "REF-006_Milewski_2019_CategoryTheoryForProgrammers.pdf"

# Shalizi & Crutchfield 2001 - Computational Mechanics
dl "REF-084" "https://arxiv.org/pdf/cond-mat/9907176" "REF-084_Shalizi_Crutchfield_2001_ComputationalMechanics.pdf"

# Clark & Chalmers 1998 - Extended Mind
dl "REF-063" "http://consc.net/papers/extended.pdf" "REF-063_Clark_Chalmers_1998_ExtendedMind.pdf"

# Cousot & Cousot 1977 - Abstract Interpretation
dl "REF-074" "https://www.di.ens.fr/~cousot/COUSOTpapers/POPL77.shtml" "SKIP_REF-074"
dl "REF-074" "https://www.di.ens.fr/~cousot/publications.www/CousijotCousot-POPL-77-ACM-p238--252-1977.pdf" "REF-074_Cousot_1977_AbstractInterpretation.pdf"

# Engeström 1987 - Learning by Expanding (author made it free)
dl "REF-094" "http://lchc.ucsd.edu/mca/Paper/Engestrom/Learning-by-Expanding.pdf" "REF-094_Engestrom_1987_LearningByExpanding.pdf"

# Scott 1970 - Outline of Mathematical Theory of Computation
dl "REF-022" "https://ropas.snu.ac.kr/lib/dock/Sc70.pdf" "REF-022_Scott_1970_MathTheoryComputation.pdf"

# Wilson 2007 - Rethinking Sociobiology
dl "REF-104" "https://evolution-institute.org/wp-content/uploads/2015/08/Rethinking-sociobiology.pdf" "REF-104_Wilson_Wilson_2007_RethinkingSociobiology.pdf"

# Turney 2008 - Uniform Approach to Analogies
dl "REF-090" "https://arxiv.org/pdf/0809.0124" "REF-090_Turney_2008_UniformApproachAnalogies.pdf"

# Onsager 1931 - Reciprocal Relations
dl "REF-031" "https://faculty.washington.edu/ghMDRtm/Handouts/Onsager1.pdf" "REF-031_Onsager_1931_ReciprocalRelations.pdf"

# Crutchfield & Young 1989
dl "REF-083" "https://arxiv.org/pdf/cond-mat/9907176" "SKIP_REF-083"
# Different paper
dl "REF-083" "http://csc.ucdavis.edu/~cmg/papers/CYo89.pdf" "REF-083_Crutchfield_Young_1989_InferringStatisticalComplexity.pdf"

# Gentner 1983 - Structure Mapping
dl "REF-088" "https://groups.psych.northwestern.edu/gentner/papers/Gentner83.pdf" "REF-088_Gentner_1983_StructureMapping.pdf"

# Atkin - Peirce's Theory of Signs (SEP - free)
dl "REF-050" "https://plato.stanford.edu/entries/peirce-semiotics/" "SKIP_REF-050"
# SEP is HTML not PDF, skip for now

echo ""
echo "=== RESULTS ==="
echo "Downloaded: $downloaded"
echo "Failed:     $failed"
echo "Skipped:    $skipped"
echo ""

# Count actual PDFs
actual=$(ls -1 *.pdf 2>/dev/null | wc -l | tr -d ' ')
echo "Total PDFs in directory: $actual"
