export interface AffiliateConfig {
  paddleId: string;
  store?: string;
  page?: string;
}

export interface StoreConfig {
  baseUrl: string;
  affiliateParam: string;
  affiliateId: string;
}

const storeConfigs: Record<string, StoreConfig> = {
  'brazil-store': {
    baseUrl: 'https://brazil-store.com.br',
    affiliateParam: 'ref',
    affiliateId: 'pickleiq-123',
  },
  'dropshot': {
    baseUrl: 'https://dropshot.com.br',
    affiliateParam: 'af',
    affiliateId: 'pickleiq-456',
  },
  'mercado-livre': {
    baseUrl: 'https://mercadolivre.com.br',
    affiliateParam: 'promo',
    affiliateId: 'pickleiq-789',
  },
};

export function resolveAffiliateUrl(config: AffiliateConfig): string {
  const storeConfig = storeConfigs[config.store || 'brazil-store'];
  const url = new URL(`${storeConfig.baseUrl}/p/${config.paddleId}`);
  
  const utmParams = {
    utm_source: 'pickleiq',
    utm_medium: 'affiliate',
    utm_content: config.page || 'unknown',
    utm_campaign: 'organic',
  };

  Object.entries(utmParams).forEach(([key, value]) => {
    url.searchParams.set(key, value);
  });

  url.searchParams.set(storeConfig.affiliateParam, storeConfig.affiliateId);
  
  return url.toString();
}

export function trackAffiliateClick(paddleId: string, store: string, page: string): void {
  console.log(`[Analytics] Affiliate click - Paddle: ${paddleId}, Store: ${store}, Page: ${page}`);
}