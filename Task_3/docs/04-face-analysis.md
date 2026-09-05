# Face analysis

The default OpenCV provider detects faces with a local Haar cascade and calculates a compact normalized prototype descriptor from the primary detected crop. A cosine score is only a visual-similarity indicator; it must not be used to identify a person, make eligibility decisions, or authenticate someone.

