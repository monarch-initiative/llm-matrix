import pytest
import requests
import requests_cache
from typing import Dict, List, Optional
from dataclasses import dataclass
from urllib.parse import quote


@dataclass
class ProteinAnnotations:
    uniprot_id: str
    cautions: List[str]
    go_terms: List[str]


@pytest.mark.skip(reason="This test is not yet implemented")
def test_all():
    fetch_annotated_proteins()

def fetch_annotated_proteins() -> List[ProteinAnnotations]:
    session = requests_cache.CachedSession('uniprot_cache', expire_after=36000)
    endpoint = "https://sparql.uniprot.org/sparql"

    # Query 1: Get all reviewed human proteins
    human_query = """
    PREFIX up: <http://purl.uniprot.org/core/>
    SELECT DISTINCT ?protein
    WHERE {
        ?protein a up:Protein ;
                up:organism <http://purl.uniprot.org/taxonomy/9606> ;
                up:reviewed true .
    }
    """

    # Query 2: Get cautions for a specific protein
    caution_query = """
    PREFIX up: <http://purl.uniprot.org/core/>
    SELECT DISTINCT ?caution
    WHERE {
        <http://purl.uniprot.org/uniprot/%s> up:annotation ?anno .
        ?anno a up:Caution_Annotation ;
              rdfs:comment ?caution .
    }
    """

    # Query 3: Get GO terms for a protein with cautions
    go_query = """
    PREFIX up: <http://purl.uniprot.org/core/>
    SELECT DISTINCT ?go
    WHERE {
        <http://purl.uniprot.org/uniprot/%s> up:classifiedWith ?go .
        FILTER(regex(str(?go), "^http://purl.obolibrary.org/obo/GO_"))
    }
    """

    def run_query(query: str) -> List[Dict]:
        headers = {'Accept': 'application/sparql-results+json'}
        print(query)
        response = session.get(
            endpoint,
            params={'query': query},
            headers=headers
        )
        response.raise_for_status()
        return response.json()['results']['bindings']

    results = []

    # Get all human proteins
    human_results = run_query(human_query)

    for protein_result in human_results:
        print(protein_result)
        raise ValueError(f"Protein result: {protein_result}")
        protein_uri = protein_result['protein']['value']
        uniprot_id = protein_uri.split('/')[-1]

        # Get cautions for this protein
        formatted_caution_query = caution_query % uniprot_id
        caution_results = run_query(formatted_caution_query)

        cautions = [r['caution']['value'] for r in caution_results]

        # Only get GO terms if cautions exist
        go_terms = []
        if cautions:
            formatted_go_query = go_query % uniprot_id
            go_results = run_query(formatted_go_query)
            go_terms = [r['go']['value'].split('GO_')[1] for r in go_results]

        results.append(ProteinAnnotations(
            uniprot_id=uniprot_id,
            cautions=cautions,
            go_terms=go_terms
        ))

    return results


# Usage example:
if __name__ == "__main__":
    annotated_proteins = fetch_annotated_proteins()
    for protein in annotated_proteins:
        if protein.cautions:  # Only print proteins with cautions
            print(f"\nProtein: {protein.uniprot_id}")
            print("Cautions:")
            for caution in protein.cautions:
                print(f"  - {caution}")
            print("GO terms:", ", ".join(protein.go_terms))