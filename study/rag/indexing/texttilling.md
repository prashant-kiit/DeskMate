TextTiling(Document)

1. Split document into small blocks
   B1, B2, B3, ..., Bn

2. For every adjacent pair:
      calculate similarity(Bi, Bi+1)

3. Store the similarity scores:
      S = [s1, s2, s3, ..., sn-1]

4. Find positions where similarity is LOW
   → these are candidate topic boundaries

5. Select significant low-similarity points

6. Split the document at those boundaries

7. Return topic segments