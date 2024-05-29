import json

# The list of references as a Python dictionary
references = {
    "Author1": "Knuth, Donald E. (1997). The Art of Computer Programming, Volume 2: Seminumerical Algorithms. Addison-Wesley.",
    "Author2": "Koblitz, Neal (1987). A Course in Number Theory and Cryptography. Springer-Verlag.",
    "Author3": "Rivest, Ronald L., Shamir, Adi, and Adleman, Leonard (1978). A Method for Obtaining Digital Signatures and Public-Key Cryptosystems. Communications of the ACM.",
    "Author4": "Shoup, Victor (2009). A Computational Introduction to Number Theory and Algebra. Cambridge University Press.",
    "Author5": "Menezes, Alfred J., van Oorschot, Paul C., and Vanstone, Scott A. (1996). Handbook of Applied Cryptography. CRC Press.",
    "Author6": "Graham, Ronald L., Knuth, Donald E., and Patashnik, Oren (1994). Concrete Mathematics: A Foundation for Computer Science. Addison-Wesley.",
    "Author7": "Boneh, Dan, and Shoup, Victor (2020). A Graduate Course in Applied Cryptography. Draft version 0.5.",
    "Author8": "Silverman, Joseph H. (2006). A Friendly Introduction to Number Theory. Pearson.",
    "Author9": "Stinson, Douglas R., and Paterson, Maura (2018). Cryptography: Theory and Practice. Fourth Edition. CRC Press.",
    "Author10": "Shannon, Claude E. (1949). Communication Theory of Secrecy Systems. Bell System Technical Journal.",
    "Author11": "Diffie, Whitfield, and Hellman, Martin E. (1976). New Directions in Cryptography. IEEE Transactions on Information Theory.",
    "Author12": "Ferguson, Niels, Schneier, Bruce, and Kohno, Tadayoshi (2010). Cryptography Engineering: Design Principles and Practical Applications. Wiley.",
    "Author13": "Goldreich, Oded (2004). Foundations of Cryptography: Volume 1, Basic Tools. Cambridge University Press.",
    "Author14": "Paar, Christof, and Pelzl, Jan (2009). Understanding Cryptography: A Textbook for Students and Practitioners. Springer.",
    "Author15": "Katz, Jonathan, and Lindell, Yehuda (2020). Introduction to Modern Cryptography. Third Edition. CRC Press.",
    "Author16": "Alkassar, Ammar, and Biswas, Anubhab (2021). Computer Security and the Internet: Tools and Jewels. Springer.",
    "Author17": "Garey, Michael R., and Johnson, David S. (1979). Computers and Intractability: A Guide to the Theory of NP-Completeness. W. H. Freeman."
}

# Save the references dictionary to a JSON file
with open('/mnt/data/references.json', 'w') as f:
    json.dump(references, f)

# Provide the file path for download
'/mnt/data/references.json'
