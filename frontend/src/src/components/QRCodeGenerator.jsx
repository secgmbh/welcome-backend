import { QRCodeSVG } from 'qrcode.react';
import { Download } from 'lucide-react';

/**
 * QR Code Generator Component
 * 
 * Usage:
 * <QRCodeGenerator value="https://welcome-link.de/property/123" />
 */
export default function QRCodeGenerator({ 
  value, 
  size = 256, 
  level = 'H',
  includeDownload = true,
  includeImage = true,
  className = ''
}) {
  const downloadQRCode = () => {
    const svg = document.getElementById('qr-code-svg');
    const svgData = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    canvas.width = size;
    canvas.height = size;

    img.onload = () => {
      ctx.drawImage(img, 0, 0);
      const pngFile = canvas.toDataURL('image/png');
      
      const downloadLink = document.createElement('a');
      downloadLink.download = 'qr-code.png';
      downloadLink.href = pngFile;
      downloadLink.click();

      // Track download
      if (window.posthog) {
        window.posthog.capture('qr_code_downloaded', { value });
      }
    };

    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
  };

  return (
    <div className={`flex flex-col items-center gap-4 ${className}`}>
      <div className="p-4 bg-white rounded-lg shadow-lg">
        <QRCodeSVG
          id="qr-code-svg"
          value={value}
          size={size}
          level={level}
          includeMargin={true}
          imageSettings={includeImage ? {
            src: '/logo192.png',
            x: undefined,
            y: undefined,
            height: size * 0.2,
            width: size * 0.2,
            excavate: true,
          } : undefined}
        />
      </div>
      
      {includeDownload && (
        <button
          onClick={downloadQRCode}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
        >
          <Download className="h-4 w-4" />
          QR-Code herunterladen
        </button>
      )}
    </div>
  );
}

/**
 * Generate QR Code for Property
 */
export function PropertyQRCode({ propertyId, propertyName }) {
  const url = `${window.location.origin}/property/${propertyId}`;

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          QR-Code für {propertyName}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-300">
          Gäste können diesen QR-Code scannen, um direkt zur digitalen Gästemappe zu gelangen.
        </p>
      </div>
      
      <QRCodeGenerator value={url} />
      
      <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
        {url}
      </div>
    </div>
  );
}
