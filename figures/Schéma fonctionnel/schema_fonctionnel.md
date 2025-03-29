graph TD
    A[Utilisateur] --> B[Sélectionne un fichier image]
    B --> C{Pré-traitement de l'image}
    C --> D[Redimensionnement agrandissement]
    D --> E[Conversion en niveaux de gris]
    E --> F[Thresholding]
    F --> G{Reconnaissance de texte et QR Code}
    G --> H[Tesseract OCR]
    G --> I[Pyzbar QR Code]
    H --> J[Texte brut reconnu]
    I --> K[Données du QR Code]
    J --> L{Formatage du texte par Regex}
    K --> L
    L --> M[Texte formaté]
    M --> N{Stockage en Base de Données}
    N --> O[Base de Données]
    O --> P[Onglet_Base_de_Données_Visualisation_des_résultats]
    A --> P
    O --> Q[Fonction de Monitoring]
    A --> Q
    O --> R[Page de Statistiques sur la Base de Données des Factures]
    A --> R
