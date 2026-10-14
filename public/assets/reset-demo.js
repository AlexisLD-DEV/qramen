(() => {
  const root = document.querySelector('#demo-reset');
  if (!root) return;

  root.innerHTML = '<section class="demo-reset" aria-labelledby="demo-reset-title"><h2 id="demo-reset-title">Démonstration</h2><p>Générez des commandes dans Airtable ou réinitialisez les commandes de démo.</p><div class="demo-actions"><button id="generate-open" type="button" disabled>Générer une démo</button><button id="reset-open" type="button" disabled>Réinitialiser la démo</button></div><p id="reset-result" role="status" aria-live="polite"></p><div id="generate-confirm" class="reset-confirm generate-confirm" hidden><h3>Confirmer la génération</h3><p>Quatre commandes seront ajoutées à Airtable sur des tables libres, avec des plats des deux enseignes et des états variés. Chaque confirmation ajoute un nouveau lot de 4 commandes ; les lots précédents ne sont pas remplacés.</p><div><button id="generate-cancel" type="button">Annuler</button><button id="generate-submit" type="button">Créer les 4 commandes</button></div></div><div id="reset-confirm" class="reset-confirm" hidden><h3>Confirmer la réinitialisation</h3><p>Cette action supprimera <strong>toutes les commandes et toutes leurs lignes</strong> dans Airtable et remettra les tables à « Libre ». La carte des plats reste intacte. Cette action est définitive.</p><div><button id="reset-cancel" type="button">Annuler</button><button id="reset-submit" type="button">Supprimer les commandes</button></div></div></section>';

  const $ = selector => root.querySelector(selector);
  const open = $('#reset-open'), confirm = $('#reset-confirm');
  const submit = $('#reset-submit'), cancel = $('#reset-cancel'), result = $('#reset-result');
  const generateOpen = $('#generate-open'), generateConfirm = $('#generate-confirm');
  const generateSubmit = $('#generate-submit'), generateCancel = $('#generate-cancel');
  let resetting = false, generating = false;

  open.addEventListener('click', () => {
    result.textContent = '';
    confirm.hidden = false;
    open.disabled = true;
    submit.focus();
  });
  cancel.addEventListener('click', () => {
    confirm.hidden = true;
    open.disabled = false;
  });
  submit.addEventListener('click', async () => {
    if (resetting) return;
    resetting = true;
    submit.disabled = true;
    cancel.disabled = true;
    open.disabled = true;
    generateOpen.disabled = true;
    result.textContent = 'Suppression en cours…';
    try {
      const response = await fetch(window.QRAMEN_API + '/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmation: 'REINITIALISER LA DEMO' }),
        signal: AbortSignal.timeout(30000),
      });
      const data = await response.json();
      if (!response.ok || data.ok !== true) throw Error(data.error || 'Échec du reset');
      confirm.hidden = true;
      result.textContent = `${data.commandesSupprimees} commandes supprimées · ${data.lignesSupprimees} lignes supprimées · ${data.tablesLiberees} tables libérées`;
      await window.refreshDemoView?.();
    } catch (error) {
      result.textContent = 'Échec du reset : ' + error.message;
      cancel.disabled = false;
      submit.disabled = false;
    } finally {
      resetting = false;
      generateOpen.disabled = false;
    }
  });

  generateOpen.addEventListener('click', () => {
    result.textContent = '';
    generateConfirm.hidden = false;
    generateOpen.disabled = true;
    generateSubmit.focus();
  });
  generateCancel.addEventListener('click', () => {
    generateConfirm.hidden = true;
    generateOpen.disabled = false;
  });
  generateSubmit.addEventListener('click', async () => {
    if (generating) return;
    generating = true;
    generateSubmit.disabled = true;
    generateCancel.disabled = true;
    open.disabled = true;
    generateOpen.disabled = true;
    result.textContent = 'Création des commandes en cours…';
    try {
      const response = await fetch(window.QRAMEN_API + '/demo/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirmation: 'GENERER LA DEMO' }),
        signal: AbortSignal.timeout(60000),
      });
      const data = await response.json();
      if (!response.ok || data.ok !== true) throw Error(data.error || 'Échec de la génération');
      generateConfirm.hidden = true;
      const resume = data.commandes.map(c => `#${c.numero} ${c.table} · ${c.statut}`).join(' ; ');
      result.textContent = `Vérifié dans Airtable : ${data.commandes.length} commandes, ${data.lignesVerifiees} lignes. ${resume}${data.commandes.some(c => c.additionDemandee) ? ' · addition demandée' : ''}.`;
      await window.refreshDemoView?.();
    } catch (error) {
      result.textContent = 'Échec de la génération : ' + error.message;
      generateSubmit.disabled = false;
      generateCancel.disabled = false;
    } finally {
      generating = false;
      open.disabled = false;
      generateOpen.disabled = false;
    }
  });

  window.setDemoResetEnabled = enabled => {
    open.disabled = !enabled || resetting || generating;
    generateOpen.disabled = !enabled || resetting || generating;
  };
})();
