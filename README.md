# TCM-Agent: Advancing Network Pharmacology and Herbal Medicine Discovery with LLM-Based Multi-Agent Systems

A Traditional Chinese Medicine (TCM) agent analysis system based on large language models, accelerating TCM systems pharmacology analysis and drug discovery. This system integrates multiple data sources and analytical tools, enabling compound information query, target analysis, molecular similarity calculation, enrichment analysis, and more.

## Key Features

1.  **Compound Information Query**: Retrieve detailed compound information through PubChem API, supporting chemical structures, molecular formulas, and other basic information queries.
2.  **Target Analysis**: Drug-target relationship analysis based on TTD database, protein-protein interaction network analysis.
3.  **Molecular Similarity Calculation**: Supports multiple molecular fingerprint types (Morgan, MACCS, Topological, Atom Pairs) and similarity calculation methods (Tanimoto, Dice, Cosine, etc.).
4.  **Drug-Target Activity Analysis**: Analyze drug-target binding activity with detailed activity data.
5.  **Target Enrichment Analysis**: Supports multiple enrichment analysis databases, provides downloadable enrichment analysis result files, generates detailed reports, and automatically creates visual charts.
6.  **TCM-Target Knowledge Graph**: Automatically loads and displays knowledge graphs of TCM-target relationships when conversation involves TCM target information.

## UI Design Features

The system adopts a modern design style with the following characteristics:

1.  **Visual Design**: Purple-blue gradient theme, frosted glass background, refined shadows and glow effects, responsive layout.
2.  **Interaction Experience**: Smooth animated transitions, hover feedback and status indicators, intuitive chat interface, real-time typing indicators.
3.  **Navigation System**: 
    *   **Homepage**: Top navigation bar with logo and main page links
    *   **Agent Page**: Left sidebar navigation, 64px width, fixed positioning, containing logo, navigation icons and version information
    *   **Responsive Design**: Automatically switches navigation modes based on page type for optimal user experience
4.  **Core Pages**: Visually striking homepage, professional Agent chat page (supports Markdown rendering), full-screen layout optimization.
5.  **Data Visualization**: 
    *   **Agent Page**: Right-side panel simultaneously displays **enrichment analysis result images and TCM-target knowledge graphs**. When both visualizations are triggered, they display in **vertical arrangement** without interference.
    *   **Responsive Layout**: Page supports vertical scrolling. When both knowledge graphs and images are displayed, page height automatically expands. Users can scroll to view full content. Knowledge graph height is 450px, image panel height is 600px, ensuring clear chart visibility.
    *   **Full-Screen Image View**: Enrichment analysis charts support click-to-zoom full-screen viewing with dedicated zoom buttons.
    *   **File Downloads**: Supports multiple file formats (`.xlsx`, `.csv`, `.pdf`, `.json`, `.zip`).
6.  **User Interaction Controls**:
    *   **Input Area Control Bar**: Model selector, clear chat history button, scroll-to-bottom button concentrated above input box.
    *   **Responsive Layout**: Chat area automatically adjusts width when right panel appears.
    *   **Status Indicators**: Clear visual feedback with button hover effects and state changes.

## System Architecture

-   **Frontend**: React (TypeScript) + Material UI
-   **Backend**: Python Flask + Socket.IO
-   **Communication**: WebSocket + RESTful API
-   **Models**: Supports multiple LLMs (e.g., Deepseek, Doubao)

## API Interfaces

### WebSocket Interfaces
- `ask_question`: Submit questions, receive streaming answers
- `question_answer`: Receive AI answer fragments
- `stream_end`: Marks answer completion

### RESTful API Interfaces
- `POST /api/reset_conversation`: Reset conversation history (clears chat history on frontend and backend)

## Project Structure
