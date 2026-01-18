import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

/**
 * PDF Export Utilities
 */

/**
 * Export HTML element as PDF
 */
export const exportElementToPDF = async (elementId, filename = 'document.pdf', options = {}) => {
  const element = document.getElementById(elementId);
  
  if (!element) {
    console.error(`Element with id "${elementId}" not found`);
    return false;
  }

  try {
    // Convert HTML to canvas
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      logging: false,
      ...options
    });

    const imgData = canvas.toDataURL('image/png');
    
    // Calculate PDF dimensions
    const imgWidth = 210; // A4 width in mm
    const pageHeight = 297; // A4 height in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;

    // Create PDF
    const pdf = new jsPDF('p', 'mm', 'a4');
    let position = 0;

    // Add image to PDF (handle multiple pages if needed)
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft >= 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    // Save PDF
    pdf.save(filename);

    // Track export
    if (window.posthog) {
      window.posthog.capture('pdf_exported', { filename });
    }

    return true;
  } catch (error) {
    console.error('PDF export failed:', error);
    return false;
  }
};

/**
 * Generate property guest guide PDF
 */
export const exportGuestGuidePDF = async (propertyData) => {
  const { name, address, checkin, checkout, wifi, contacts, amenities, rules } = propertyData;

  const pdf = new jsPDF();
  let yPosition = 20;

  // Title
  pdf.setFontSize(22);
  pdf.setFont('helvetica', 'bold');
  pdf.text(`Willkommen bei ${name}`, 20, yPosition);
  yPosition += 15;

  // Address
  pdf.setFontSize(12);
  pdf.setFont('helvetica', 'normal');
  pdf.text(address, 20, yPosition);
  yPosition += 10;

  // Check-in/Check-out
  pdf.setFontSize(14);
  pdf.setFont('helvetica', 'bold');
  pdf.text('Check-in & Check-out', 20, yPosition);
  yPosition += 8;
  
  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'normal');
  pdf.text(`Check-in: ${checkin}`, 20, yPosition);
  yPosition += 6;
  pdf.text(`Check-out: ${checkout}`, 20, yPosition);
  yPosition += 12;

  // WiFi
  if (wifi) {
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.text('WiFi', 20, yPosition);
    yPosition += 8;
    
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`Netzwerk: ${wifi.ssid}`, 20, yPosition);
    yPosition += 6;
    pdf.text(`Passwort: ${wifi.password}`, 20, yPosition);
    yPosition += 12;
  }

  // Contacts
  if (contacts && contacts.length > 0) {
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Kontakte', 20, yPosition);
    yPosition += 8;
    
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'normal');
    contacts.forEach(contact => {
      pdf.text(`${contact.name}: ${contact.phone}`, 20, yPosition);
      yPosition += 6;
    });
    yPosition += 6;
  }

  // Add new page if needed
  if (yPosition > 250) {
    pdf.addPage();
    yPosition = 20;
  }

  // Amenities
  if (amenities && amenities.length > 0) {
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Ausstattung', 20, yPosition);
    yPosition += 8;
    
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'normal');
    amenities.forEach(amenity => {
      pdf.text(`• ${amenity}`, 25, yPosition);
      yPosition += 6;
    });
    yPosition += 6;
  }

  // House Rules
  if (rules && rules.length > 0) {
    if (yPosition > 230) {
      pdf.addPage();
      yPosition = 20;
    }

    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Hausregeln', 20, yPosition);
    yPosition += 8;
    
    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'normal');
    rules.forEach(rule => {
      pdf.text(`• ${rule}`, 25, yPosition);
      yPosition += 6;
    });
  }

  // Footer
  const pageCount = pdf.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    pdf.setPage(i);
    pdf.setFontSize(9);
    pdf.setFont('helvetica', 'italic');
    pdf.text(
      `Erstellt mit Welcome Link - Seite ${i} von ${pageCount}`,
      105,
      290,
      { align: 'center' }
    );
  }

  // Save
  const filename = `${name.replace(/\s+/g, '_')}_Gästemappe.pdf`;
  pdf.save(filename);

  // Track
  if (window.posthog) {
    window.posthog.capture('guest_guide_pdf_exported', { 
      property_name: name 
    });
  }

  return true;
};

/**
 * Print current page
 */
export const printPage = () => {
  window.print();
  
  if (window.posthog) {
    window.posthog.capture('page_printed');
  }
};

export default {
  exportElementToPDF,
  exportGuestGuidePDF,
  printPage
};
