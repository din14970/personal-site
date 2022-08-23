Title: Saving PDF files with a CMYK color profile with Inkscape in 2022
Date: 2022-08-23 13:40
Category: Design
Tags: inkscape, color, cmyk, scribus, pdf, rgb
Summary: CMYK is still a pain in Inkscape but there is a way to get close


I made a card to announce the birth of my daughter using the open source vector editing software [Inkscape](https://inkscape.org/).
Unfortunately when I took the PDF export to the print shop, all the colors came out looking terrible and dark.
Turns out Inkscape works internally only with RGB colors, but print shops expect colors to be encoded in CMYK format.
The values you see on the screen will always be RGB because that is how the screen should represent the colors.
Even though confusingly you can select colors in CMYK in the "Fill and stroke" menu, this will not correspond to the actual CMYK colors in print, because Inkscape likely uses a different look up table.
The devs seem [to acknowledge this](https://gitlab.com/inkscape/inkscape/-/issues/2184) and it seems to be a feature that is actively being worked on.

The CMYK issue is long standing and has had multiple proposed workarounds, see for example [logos by nick](https://logosbynick.com/export-cmyk-with-inkscape/).
However, I found that most of these solutions are outdated, or did not apply given that the printshop would only accept a PDF.
From that same page, I found that the `ExportPDFCMYK` extension did not work and the [Scribus method](https://www.youtube.com/watch?v=RNkWXwk_H8o) seemed outdated and tedious.
The scribus method is also detailed [here](https://www.klaasnotfound.com/2016/06/05/creating-cmyk-prepress-pdfs-with-inkscape-and-scribus/); again super tedious.

There is a "quick" way to do it however for which I found no explanatory resources online.
This works on Linux, more specifically Arch.
If you have Scribus installed on your system, it will also be possible to select `Scribus CMYK PDF (*.PDF)` in the `Save As...` menu in Inkscape.
This will bring up a dialog that allows you to do a quick export to a PDF with CMYK color profile.
You will get a very cryptic error though if you try this.
In order to get it to work, you should go into `File > Document Properties > Color` and select a color profile, like `sRGB-elle-V2-g10.icc`.
You may also need to install the python module `cssselect` in the system python environment, otherwise you may also get an error.
Once you click save, Scribus should briefly open, close again, and your pdf should be saved.

Some notes here: not all RGB colors can be safely converted to CMYK.
Some colors are simply too bright or saturated and can't be adequately represented in the color space.
This conversion does not take this into account and you may need to modify the colors in the original drawing, which can be a painful iterative process.
You can view colors out of CMYK range in Scribus by going to `Preferences > Color Management` and selecting `Mark Colors out of Gamut`.
Out of range colors will show up as bright green.
Some nice information to do this in the best way can be found [here](https://librearts.org/2011/09/how-to-get-cmyk-colors-from-inkscape-to-scribus/).

Additionally, pay attention that there are a lot of features in Inkscape that result in visually fine looking PDFs but which can not be interpreted properly in print.
I would recommend to stay away from `Filters` to create your image - some filters further modify the visual colors, but not the underlying colors.
Always choose colors directly in the color picker.
