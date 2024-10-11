---

title: 'ChemParse: A User-Centric Tool for Parsing Computational Chemistry Outputs'
tags:
  - Python
  - computational chemistry
  - data parsing
  - ORCA
  - GPAW
  - VASP
authors:
  - name: Ivan Tambovtsev
    orcid: 0000-0001-9223-8961
    affiliation: 1
affiliations:
 - name: Science Institute and Faculty of Physical Sciences, University of Iceland, 107 Reykjav\'{\i}k, Iceland
   index: 1
date: 13 September 2024
bibliography: paper.bib

# Summary

ChemParse is a tool designed to enhance the parsing of computational chemistry outputs, addressing the need for accessible data handling capabilities. Existing tools such as cclib [@oboyleCclibLibraryPackageindependent2008], ASE [@larsenAtomicSimulationEnvironment2017; @bahnObjectorientedScriptingInterface2002], and NOMAD [@scheidgenNOMADDistributedWebbased2023] require significant developer expertise for adaptation and extension, which can be a barrier for researchers with limited programming knowledge. ChemParse mitigates this by allowing users to define custom extraction patterns through a user-friendly interface, making the parsing process more accessible. The tool supports data from various computational chemistry software, including ORCA [@neeseORCAProgramSystem2012; @neeseSoftwareUpdateORCA2018; @neeseSoftwareUpdateORCA2022], GPAW [@enkovaaraElectronicStructureCalculations2010], and VASP [@kresseEfficientIterativeSchemes1996; @kresseEfficiencyAbinitioTotal1996], but is not limited to these sources.

The architecture of ChemParse emphasizes simplicity and flexibility, supporting user-driven development and facilitating contributions from a broad user base. This adaptability is complemented by features that convert outputs into interactive HTML documents, alongside a two-part system that separates output blocks identification from the data extraction. This method enhances the reliability of the parsing process compared to traditional methods and promotes a collaborative environment through community contributions.

ChemParse contributes to the field of computational chemistry by providing a tool that is both accessible and effective, addressing the evolving needs of the scientific community.

# Statement of need

The field of computational chemistry relies heavily on sophisticated tools to parse and interpret output data from various quantum chemistry software packages. Those tools often require extensive developer expertise to adapt to new software outputs or integrate additional features. This dependency creates a significant barrier for researchers, particularly those without advanced programming skills, who need to customize data extraction for their specific research needs.

ChemParse addresses these challenges by providing a more accessible, user-centric tool that simplifies the process of customizing and extending data extraction capabilities. It enables researchers to define custom extraction patterns through an intuitive interface, without needing to engage deeply with the underlying codebase. This feature is particularly beneficial in a field where output formats are continually evolving and where the ability to adapt parsing strategies quickly can significantly enhance research efficiency and effectiveness.

Moreover, the existing tools' complex and rigid structure often discourages contributions from the broader scientific community. ChemParse, with its emphasis on user-driven development and simplicity, not only facilitates easier customization but also encourages contributions, making it a living repository of collective scientific knowledge. By lowering the entry barrier for adding new functionalities, ChemParse enhances the collaborative spirit within the scientific community, fostering a more inclusive environment for innovation and development in computational chemistry.


# Software description

ChemParse is a computational chemistry tool designed to enhance the data extraction process from quantum chemistry software outputs. Its architecture promotes flexibility and user-friendliness, encouraging contributions from researchers across a wide spectrum of programming expertise. The software operates primarily through a two-part system aimed at efficient and precise data handling.

The first component of ChemParse involves the use of regular expressions (regex) to identify distinct data blocks within output files. This step ensures that the data is organized into contextually coherent blocks, laying the groundwork for accurate data extraction. Recognizing the complexity regex might pose for non-programmers, ChemParse introduces "blueprints." These are user-friendly templates that allow users to easily generate new regex patterns tailored to their specific needs without requiring in-depth knowledge of regex syntax.

Following the identification of data blocks, the second component of ChemParse is activated—specific data extraction. This process is only performed upon user request for the specific block data extraction, optimizing the tool's performance and ensuring that the extraction does not become a bottleneck, even when handling large datasets. The data blocks' manageable size contributes to the system's overall efficiency and reliability.

Additionally, ChemParse can transform output files into interactive HTML documents with CSS and JavaScript to improve data visualization and make it easier for users to navigate and analyze results.


# Acknowledgements

This work was funded by the Icelandic Research Fund (grant 239970).

# References

---
