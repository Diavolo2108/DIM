export const metadata = { title: "Política de Privacidad — Diavolo Social Manager" };

export default function PrivacidadPage() {
  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "48px 24px", fontFamily: "sans-serif", color: "#111" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>Política de Privacidad</h1>
      <p style={{ color: "#666", marginBottom: 32 }}>Diavolo Social Manager · Última actualización: mayo 2026</p>

      <section style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>1. Información que recopilamos</h2>
        <p>Diavolo Social Manager ("la aplicación") recopila la siguiente información para prestar sus servicios:</p>
        <ul style={{ paddingLeft: 20, lineHeight: 2 }}>
          <li>Nombre de usuario y dirección de correo electrónico del administrador</li>
          <li>Tokens de acceso de cuentas de Instagram conectadas</li>
          <li>Contenido de publicaciones, imágenes y videos gestionados a través de la plataforma</li>
          <li>Métricas de rendimiento de las cuentas conectadas (alcance, impresiones, seguidores)</li>
          <li>Mensajes directos y comentarios de Instagram procesados por el sistema</li>
        </ul>
      </section>

      <section style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>2. Cómo usamos la información</h2>
        <ul style={{ paddingLeft: 20, lineHeight: 2 }}>
          <li>Publicar contenido en Instagram en nombre del usuario autorizado</li>
          <li>Gestionar y responder mensajes directos y comentarios</li>
          <li>Generar reportes de métricas y análisis de rendimiento</li>
          <li>Planificar campañas de marketing con asistencia de inteligencia artificial</li>
        </ul>
      </section>

      <section style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>3. Compartición de datos</h2>
        <p>No vendemos ni compartimos tu información personal con terceros, excepto con los siguientes proveedores necesarios para operar el servicio:</p>
        <ul style={{ paddingLeft: 20, lineHeight: 2 }}>
          <li><strong>Meta (Facebook/Instagram)</strong> — para acceder a las cuentas autorizadas mediante la API oficial</li>
          <li><strong>Anthropic</strong> — para generación de contenido con inteligencia artificial</li>
          <li><strong>Cloudflare</strong> — para almacenamiento de archivos multimedia</li>
          <li><strong>Supabase</strong> — para almacenamiento de datos en base de datos cifrada</li>
        </ul>
      </section>

      <section style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>4. Seguridad de los datos</h2>
        <p>Todos los tokens de acceso y credenciales se almacenan cifrados usando encriptación AES-256. El acceso a la plataforma está protegido mediante autenticación con contraseña y tokens JWT de corta duración.</p>
      </section>

      <section style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>5. Retención de datos</h2>
        <p>Los datos se conservan mientras la cuenta esté activa. Al eliminar un cliente del sistema, sus credenciales e información asociada se eliminan de la base de datos. Puedes solicitar la eliminación completa de tus datos escribiendo a <strong>hola@diavolo.me</strong>.</p>
      </section>

      <section style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>6. Eliminación de datos de usuario</h2>
        <p>Para solicitar la eliminación de todos tus datos de la plataforma, envía un correo a <strong>hola@diavolo.me</strong> con el asunto "Eliminación de datos". Procesaremos tu solicitud en un plazo de 30 días.</p>
      </section>

      <section style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>7. Uso de la API de Meta</h2>
        <p>Esta aplicación utiliza la API de Instagram Graph de Meta para gestionar cuentas de Instagram Business autorizadas. El acceso se realiza exclusivamente con el consentimiento explícito del titular de cada cuenta. Los datos obtenidos a través de la API de Meta se utilizan únicamente para los fines descritos en esta política y no se comparten con terceros no autorizados.</p>
      </section>

      <section style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>8. Contacto</h2>
        <p>Para cualquier consulta sobre esta política de privacidad:</p>
        <ul style={{ paddingLeft: 20, lineHeight: 2 }}>
          <li>Correo: <strong>hola@diavolo.me</strong></li>
          <li>Sitio web: <strong>https://diavolo.me</strong></li>
          <li>Responsable: Jorge Alberto Mora González</li>
        </ul>
      </section>
    </div>
  );
}
