import { Resend } from 'resend';

function getResendClient() {
  return new Resend(process.env.RESEND_API_KEY);
}

export async function sendPriceAlert({
  email,
  paddleName,
  currentPrice,
  priceTarget,
  paddleUrl,
  userId,
}: {
  email: string;
  paddleName: string;
  currentPrice: number;
  priceTarget: number;
  paddleUrl: string;
  userId: string;
}) {
  const resend = getResendClient();
  return await resend.emails.send({
    from: 'alerts@pickleiq.com',
    to: email,
    subject: `Alerta de preço: ${paddleName}`,
    html: `
      <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #1a1a1a;">Ótima notícia! 🎉</h2>
        <p>
          <strong>${paddleName}</strong> agora custa
          <strong>R$ ${currentPrice.toFixed(2)}</strong> —
          abaixo do seu alvo de R$ ${priceTarget.toFixed(2)}.
        </p>
        <p style="margin: 24px 0;">
          <a href="${paddleUrl}"
             style="background: #10b981; color: white; padding: 12px 24px;
                    text-decoration: none; border-radius: 6px; font-weight: bold;">
            Ver raquete
          </a>
        </p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 32px 0;" />
        <p style="font-size: 12px; color: #9ca3af;">
          Você recebeu este email porque criou um alerta de preço no PickleIQ.<br />
          <a href="https://pickleiq.com/api/unsubscribe?user_id=${userId}"
             style="color: #6b7280;">
            Desinscrever dos alertas de preço
          </a>
        </p>
      </div>
    `,
    headers: {
      'List-Unsubscribe': `<https://pickleiq.com/api/unsubscribe?user_id=${userId}>`,
      'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
    },
  });
}
