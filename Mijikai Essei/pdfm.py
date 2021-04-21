import itertools as itt
import sys

import PyPDF2 as PDF


def main():
    fbase = sys.argv[1]

    pdf_out = PDF.PdfFileWriter()
# anything_1 is odd page, anything_2 is even page.
# use command py pdfm.py name will merge name_1.pdf and name_2.pdf into name.pdf
    with open(fbase + "_1.pdf", 'rb') as f_odd:
        with open(fbase + "_2.pdf", 'rb')  as f_even:
            pdf_odd = PDF.PdfFileReader(f_odd)
            pdf_even = PDF.PdfFileReader(f_even)

            for p in itt.chain.from_iterable(
                itt.zip_longest(
                    pdf_odd.pages,
                    reversed(pdf_even.pages),
                )
            ):
                if p:
                    pdf_out.addPage(p)

            with open(fbase + ".pdf", 'wb') as f_out:
                pdf_out.write(f_out)

    return 0


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Wrong number of arguments!")
        sys.exit(1)

    sys.exit(main())


'''
With the two scan PDFs named as doc_odd.pdf and doc_even.pdf,
 running the following scanmerge.py script (also posted as a Gist)
 as “> python scanmerge.py doc” produces the desired doc.pdf 
 with the pages nicely interleaved, and in the correct order
'''
