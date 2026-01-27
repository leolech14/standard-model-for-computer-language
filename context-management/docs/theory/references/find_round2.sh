#!/bin/bash
# Round 2: Try CORE API, PhilArchive, PMC, and curated direct URLs
DEST="/Users/lech/PROJECTS_all/PROJECT_elements/context-management/docs/theory/references"
cd "$DEST"

downloaded=0
failed=0

dl() {
    local id="$1" url="$2" filename="$3"
    [ -f "$filename" ] && { echo "  SKIP $id (exists)"; return 0; }
    echo "  GET  $id -> $filename"
    curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" --max-time 45 -o "$filename" "$url" 2>/dev/null
    if file -b "$filename" | grep -qi "pdf"; then
        local sz=$(wc -c < "$filename" | xargs)
        if [ "$sz" -gt 1000 ]; then
            echo "       OK ($sz bytes)"
            ((downloaded++))
            return 0
        fi
    fi
    rm -f "$filename" 2>/dev/null
    ((failed++))
    return 1
}

echo "=== ROUND 2: Extended Search ==="
echo ""

echo "--- CORE API search ---"
core_search() {
    local id="$1" query="$2" filename="$3"
    [ -f "$filename" ] && { echo "  SKIP $id (exists)"; return; }
    local result=$(curl -s "https://api.core.ac.uk/v3/search/works?q=${query}&limit=1" -H "Accept: application/json" 2>/dev/null)
    local pdf_url=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('results',[]); print(r[0]['downloadUrl'] if r and r[0].get('downloadUrl') else '')" 2>/dev/null)
    if [ -n "$pdf_url" ] && [ "$pdf_url" != "None" ]; then
        echo "  CORE found: $pdf_url"
        dl "$id" "$pdf_url" "$filename"
    else
        echo "  CORE: nothing for $id"
    fi
    sleep 1
}

# Philosophy papers via CORE
core_search "REF-056" "Ladyman+structural+realism+1998" "REF-056_Ladyman_1998_StructuralRealism.pdf"
core_search "REF-058" "Williams+1953+elements+being" "REF-058_Williams_1953_ElementsOfBeing.pdf"
core_search "REF-061" "French+Ladyman+2011+ontic+structural+realism" "REF-061_French_Ladyman_2011_OnticStructuralRealism.pdf"
core_search "REF-064" "Davidson+1963+actions+reasons+causes" "REF-064_Davidson_1963_ActionsReasonsCauses.pdf"
core_search "REF-047" "Lotman+1984+semiosphere" "REF-047_Lotman_1984_Semiosphere.pdf"
core_search "REF-085" "Langton+1990+computation+edge+chaos" "REF-085_Langton_1990_EdgeOfChaos.pdf"
core_search "REF-091" "Gibson+1977+theory+affordances" "REF-091_Gibson_1977_TheoryAffordances.pdf"
core_search "REF-104" "Wilson+Wilson+2007+rethinking+sociobiology" "REF-104_Wilson_2007_RethinkingSociobiology.pdf"
core_search "REF-110" "Arthur+1989+competing+technologies+lock-in" "REF-110_Arthur_1989_CompetingTechnologies.pdf"
core_search "REF-096" "Sweller+1988+cognitive+load+problem+solving" "REF-096_Sweller_1988_CognitiveLoad.pdf"
core_search "REF-075" "Clarke+1986+automatic+verification+finite+state" "REF-075_Clarke_1986_AutomaticVerification.pdf"
core_search "REF-077" "Back+1988+calculus+refinements" "REF-077_Back_1988_CalculusRefinements.pdf"
core_search "REF-113" "Myerson+1981+optimal+auction+design" "REF-113_Myerson_1981_OptimalAuctionDesign.pdf"
core_search "REF-117" "Hjorland+2008+knowledge+organization" "REF-117_Hjorland_2008_KnowledgeOrganization.pdf"
core_search "REF-115" "Krogstie+2006+process+models+knowledge" "REF-115_Krogstie_2006_ProcessModels.pdf"
core_search "REF-120" "Stiny+1980+shape+grammars" "REF-120_Stiny_1980_ShapeGrammars.pdf"
core_search "REF-028" "Bejan+1997+constructal+conducting+paths" "REF-028_Bejan_1997_ConstructalLaw.pdf"
core_search "REF-034" "Wilson+1971+renormalization+group+critical+phenomena" "REF-034_Wilson_1971_RenormalizationGroup.pdf"
core_search "REF-076" "Manna+Waldinger+1980+deductive+program+synthesis" "REF-076_Manna_1980_ProgramSynthesis.pdf"
core_search "REF-041" "Friston+2017+active+inference+learning" "REF-041_Friston_2017_ActiveInference.pdf"

echo ""
echo "--- Direct known URLs (curated) ---"

# Kalman 1960 - already have as REF-122, but confirm
dl "REF-122" "https://www.cs.unc.edu/~welch/kalman/media/pdf/Kalman1960.pdf" "REF-122_Kalman_1960_NewApproachLinear.pdf"

# Lyapunov 1892 - translated
dl "REF-124" "https://www.math.u-szeged.hu/ejqtde/Lyapunov.pdf" "REF-124_Lyapunov_1892_StabilityOfMotion.pdf"
dl "REF-124" "https://web.archive.org/web/2023/https://www.math.u-szeged.hu/ejqtde/Lyapunov.pdf" "REF-124_Lyapunov_1892_StabilityOfMotion.pdf"

# Montague 1970 - Universal Grammar
dl "REF-125" "https://www.jstor.org/stable/20114574" "SKIP_125"
core_search "REF-125" "Montague+1970+universal+grammar+theoria" "REF-125_Montague_1970_UniversalGrammar.pdf"

# Kolmogorov 1965 - three approaches
dl "REF-026" "https://www.sciencedirect.com/science/article/pii/S0019995865902414/pdf" "REF-026_Kolmogorov_1965_ThreeApproaches.pdf"
core_search "REF-026" "Kolmogorov+1965+three+approaches+quantitative+information" "REF-026_Kolmogorov_1965_ThreeApproaches.pdf"

# Tarski 1933
dl "REF-051" "https://web.archive.org/web/2024/https://www.hist-analytic.com/Tarski.pdf" "REF-051_Tarski_1933_ConceptTruth.pdf"
core_search "REF-051" "Tarski+1933+concept+truth+formalized+languages" "REF-051_Tarski_1933_ConceptTruth.pdf"

# Frege 1892
core_search "REF-059" "Frege+1892+sense+reference+bedeutung" "REF-059_Frege_1892_SenseAndReference.pdf"

# Williams 1953 - On Elements of Being
dl "REF-058" "https://www.jstor.org/stable/20123381" "SKIP_058"

# Ashby 1956 - we have this already

# Wiener 1948 - Cybernetics
dl "REF-123" "https://uberty.org/wp-content/uploads/2015/07/Norbert_Wiener_Cybernetics.pdf" "REF-123_Wiener_1948_Cybernetics.pdf"

# Morris 1938 - Foundations of Theory of Signs
dl "REF-046" "https://archive.org/download/foundationsofthe0000morr/foundationsofthe0000morr.pdf" "REF-046_Morris_1938_FoundationsTheorySigns.pdf"
core_search "REF-046" "Morris+1938+foundations+theory+signs" "REF-046_Morris_1938_FoundationsTheorySigns.pdf"

# Lambek 1980
core_search "REF-003" "Lambek+1980+lambda+calculus+cartesian+closed" "REF-003_Lambek_1980_LambdaCalculus.pdf"

# Freeman & Pfenning 1991 - we have via SS

echo ""
echo "--- PMC (biomedical) ---"
# Friston 2017 Active Inference via PMC
dl "REF-041" "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5610010/pdf/nihms891091.pdf" "REF-041_Friston_2017_ActiveInference.pdf"

# Wilson & Wilson 2007 via PMC
dl "REF-104" "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2654773/pdf/nihms-88147.pdf" "REF-104_Wilson_2007_RethinkingSociobiology.pdf"

echo ""
rm -f SKIP_* 2>/dev/null
echo "=== RESULTS ==="
echo "New downloads: $downloaded"
echo "Failed: $failed"
echo "Total PDFs: $(ls -1 *.pdf 2>/dev/null | wc -l)"
