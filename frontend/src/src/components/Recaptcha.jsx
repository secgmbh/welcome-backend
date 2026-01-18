import ReCAPTCHA from 'react-google-recaptcha';
import { useRef } from 'react';

/**
 * ReCAPTCHA Component Wrapper
 * 
 * Usage:
 * <Recaptcha onVerify={(token) => console.log(token)} />
 */
export default function Recaptcha({ onVerify, theme = 'light', size = 'normal' }) {
  const recaptchaRef = useRef(null);

  const handleChange = (token) => {
    if (token) {
      onVerify(token);
      
      // Track captcha completion
      if (window.posthog) {
        window.posthog.capture('captcha_completed');
      }
    }
  };

  const handleExpired = () => {
    console.log('reCAPTCHA expired');
    onVerify(null);
  };

  const handleError = () => {
    console.error('reCAPTCHA error');
    onVerify(null);
  };

  // Get site key from environment
  const siteKey = process.env.REACT_APP_RECAPTCHA_SITE_KEY || '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'; // Test key

  return (
    <div className="flex justify-center my-4">
      <ReCAPTCHA
        ref={recaptchaRef}
        sitekey={siteKey}
        onChange={handleChange}
        onExpired={handleExpired}
        onErrored={handleError}
        theme={theme}
        size={size}
      />
    </div>
  );
}

/**
 * Verify reCAPTCHA token on backend
 * 
 * Backend implementation needed:
 * 
 * from fastapi import HTTPException
 * import httpx
 * 
 * async def verify_recaptcha(token: str) -> bool:
 *     secret = os.getenv("RECAPTCHA_SECRET_KEY")
 *     url = "https://www.google.com/recaptcha/api/siteverify"
 *     
 *     async with httpx.AsyncClient() as client:
 *         response = await client.post(url, data={
 *             "secret": secret,
 *             "response": token
 *         })
 *         result = response.json()
 *         return result.get("success", False)
 */
