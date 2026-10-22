# Licensing Decision: CineGraph

## Recommended License: MIT License

For **CineGraph**, the recommended license for the codebase is the **MIT License**.

### Rationale

1. **Academic and Portfolio Freedom**:
   - CineGraph is an academic course project combining NoSQL database technologies (Neo4j and MonetDB).
   - The MIT License is a permissive open-source license that allows unrestricted study, distribution, and enhancement with minimal attribution requirements.

2. **Compatibility with Upstream Dependencies**:
   - **Neo4j Community Edition**: Licensed under GPLv3. Note that interacting with Neo4j via standard network protocols (Bolt / HTTP drivers) or running Neo4j in a standalone container alongside CineGraph does not trigger copyleft requirements on CineGraph's client code under common industry practice.
   - **MonetDB**: Licensed under the MonetDB Public License (MPL-based, Mozilla Public License compatible), which permits integration via client drivers.
   - **FastAPI / Pydantic / Next.js / React / Tailwind CSS**: All permissively licensed (MIT / BSD / Apache 2.0).

3. **Future Commercial / Research Flexibility**:
   - The permissive nature of MIT provides full flexibility should parts of the pipeline or architecture be extracted into future research papers, open-source packages, or commercial prototypes.
