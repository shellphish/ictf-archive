<?php

$settlement_body = 'Dear Sir/Madam:

We are forwarding this letter to you in advance of our filing a lawsuit against you in federal court for copyright infringement.  We represent a number of large record companies, as well as all of their subsidiaries and affiliates ("Record Companies").  In short, we\'re kind of a big deal.  Thus, we are pursuing claims of copyright infringement against individuals who have illegally uploaded and downloaded sound recordings or just have a cooler iPod than I do.

We have gathered evidence that you have been infringing copyrights owned by the Record Companies.  This information was gathered via our state-of-the-art copyright-infringement-awareness technology (i.e., you just told us).

The reason we are sending this letter to you in advance of filing suit is to give you the opportunity to settle these claims as early as possible.  If you contact us within the next eight (8) calendar hours, we will offer to settle the claims for a significantly reduced amount compared to what we will offer to settle them for after we file suit or compared to the judgment amount a court may enter against you.  If you are interested in resolving this matter now, please visit the MAFIA Online Piracy Settlement Center, using the CASE ID # and email address that appear at the top of this letter.

We are not your lawyers, nor are we giving you legal advice (but I have a great apple pie recipe if you\'re interested).  We urge you to consult with an attorney immediately to advise you on your rights and responsibilities.  Or you can just pay up like everyone else.';

function gen_settlement($caseid, $eaddr)
{
  require 'fpdf.php';
  global $settlement_body;

  $pdf = new FPDF('P', 'pt', 'Letter');
  $pdf->AddPage();
  $pdf->SetMargins(72, 72, 72);
  $pdf->Image('/usr/ctf/ictf-2007-amends/images/wtf.jpg', 72, 10);
  $pdf->SetFont('Times', 'B', 16);
  $pdf->Cell(0, 10, 'White Taft & Fairchild, LLP', 0, 0, 'C');
  $pdf->Ln(20);
  $pdf->SetFont('Times', 'I', 12);
  $pdf->Cell(0, 5, 'Attorneys at Law', 0, 0, 'C');
  $pdf->Ln(80);
  $pdf->SetFont('Arial', '', 12);
  $pdf->Cell(0, 5, '7 December 2007');
  $pdf->Ln(25);
  $pdf->SetFont('Arial', 'B', 12);
  $pdf->Cell(0, 5, 'Re: Notification of Copyright Infringement Claims');
  $pdf->Ln(25);
  $pdf->SetFont('Arial', '', 12);
  $pdf->Cell(0, 5, "CASE ID #: $caseid");
  $pdf->Ln(25);
  $pdf->Cell(0, 5, "Email address: $eaddr");
  $pdf->Ln(25);
  $pdf->MultiCell(0, 15, $settlement_body);
  $pdf->Ln(25);
  $pdf->Cell(0, 5, 'Sincerely,');
  $pdf->Image('/usr/ctf/ictf-2007-amends/images/hagen.jpg', 72, 645);
  $pdf->Ln(80);
  $pdf->Cell(0, 5, 'Tom Hagen');
  $pdf->Output("/usr/ctf/ictf-2007-amends/html/settlement/{$caseid}.pdf", 'F');

  return $caseid.'.pdf';
}

?>
