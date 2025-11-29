# Guía de Despliegue PostgreSQL en OpenShift / Kubernetes

## Problemas comunes y soluciones

### Problema 1: volumeMode Block vs Filesystem
**Error:** `volume postgres-data has volumeMode Block, but is specified in volumeMounts`

**Causa:** Tu PVC tiene `volumeMode: Block` (dispositivo raw), pero intentas montarlo como `volumeMounts` (filesystem).

**Soluciones:**

#### Opción A: Usar dispositivo Block con initContainer (actual)
- El `initContainer: setup-postgres-device` formatea el dispositivo Block como ext4.
- **Prerrequisito:** La SCC debe permitir `securityContext.privileged: true` o al menos `capabilities: SYS_ADMIN`.
- **Dispositivo:** Cambia `/dev/xvda` si tu dispositivo tiene otro nombre (p. ej. `/dev/sda`, `/dev/vdc`).
- **Comando para depurar:** 
  ```bash
  kubectl exec -it partner-db-pod -c setup-postgres-device -- ls -la /dev/ | grep -E "xvd|vd|sd"
  ```

#### Opción B: Cambiar PVC a volumeMode Filesystem (RECOMENDADO para simplificar)
Si quieres evitar complejidad, recrea el PVC con `volumeMode: Filesystem`:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data-pvc
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 10Gi
  volumeMode: Filesystem  # <-- Cambio clave
  storageClassName: standard  # Reemplaza con tu StorageClass
```

Luego aplica:
```bash
kubectl delete pvc postgres-data-pvc
kubectl apply -f pvc.yaml
kubectl apply -f docker/postgresql.yaml
```

#### Opción C: Usar emptyDir (sin persistencia, para pruebas rápidas)
Si el PVC Block causa muchos problemas, usa `emptyDir` en `docker/postgresql.yaml`:
```yaml
volumes:
  - name: postgres-data
    emptyDir: {}
```
⚠️ Nota: Los datos se pierden si el Pod se reinicia.

---

### Problema 2: Permisos y root_squash en NFS
**Error:** `chmod: /var/lib/postgresql/data: Operation not permitted`

**Causa:** El PV exportado por NFS tiene `root_squash` activado o permisos muy restrictivos.

**Soluciones:**
1. **Administrador del clúster:** Configura el PV/NFS sin `root_squash` o con permisos permisivos para el rango UID/GID de OpenShift.
2. **Alternativa:** Crea un subdirectorio en el PV con permisos correctos y monta ese subdirectorio (subPath).
3. **Fallback:** Usa `emptyDir` para pruebas.

---

### Problema 3: lost+found en el PV
**Error:** `initdb: directory ... exists but is not empty` debido a `lost+found`

**Causa:** El PV raíz contiene archivos de sistema de archivos.

**Soluciones:**
1. **Usar PGDATA:** Postgres usa un subdirectorio que puede estar limpio. En el manifiesto, asegúrate de incluir:
   ```yaml
   env:
     - name: PGDATA
       value: "/var/lib/postgresql/data/pgdata"
   ```
2. **Subdirectorio dedicado:** Crea un directorio dentro del PV y monta ese subdirectorio (subPath).
3. **initContainer:** Que limpie/prepara el directorio antes de que Postgres lo use.

---

## Requisitos de SCC en OpenShift

El manifiesto actual requiere:
- **`securityContext.privileged: true`** en el initContainer (para formatear dispositivos).
- Si tu SCC no permite `privileged`, consulta con tu administrador de OpenShift o usa Opción B (Filesystem PVC).

**Verificar SCC disponibles:**
```bash
oc get scc
oc describe scc <nombre>
```

---

## Despliegue paso a paso

### 1. Crear el PVC (si no existe)
```bash
# Opción Filesystem (recomendada)
cat > postgres-pvc.yaml <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data-pvc
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 10Gi
  volumeMode: Filesystem
  storageClassName: standard
EOF

kubectl apply -f postgres-pvc.yaml
```

### 2. Aplicar el manifiesto de PostgreSQL
```bash
kubectl apply -f docker/postgresql.yaml
```

### 3. Verificar el Pod
```bash
kubectl get pods -l app=partner-db
kubectl describe pod partner-db-pod
kubectl logs partner-db-pod -c setup-postgres-device    # initContainer
kubectl logs partner-db-pod -c postgres-db               # contenedor principal
```

### 4. Probar conexión (port-forward)
```bash
kubectl port-forward svc/partner-db-svc 5432:5432 &
psql -h localhost -U user -d partner_db -c "SELECT version();"
```

---

## Próximos pasos

1. **Decidir la solución definitiva:**
   - ✅ Si tienes control del clúster → Usa **Opción B** (PVC Filesystem).
   - ✅ Si el administrador permite `privileged` → Usa **Opción A** (actual, con initContainer).
   - ✅ Si solo necesitas pruebas → Usa **Opción C** (emptyDir).

2. **Configurar credenciales y secretos:**
   - El usuario/contraseña actualmente están en el manifiesto. Para producción, usa `Secrets`:
     ```yaml
     env:
       - name: POSTGRES_USER
         valueFrom:
           secretKeyRef:
             name: postgres-secret
             key: user
       - name: POSTGRES_PASSWORD
         valueFrom:
           secretKeyRef:
             name: postgres-secret
             key: password
     ```

3. **Persistencia en producción:**
   - Configura backups del PVC.
   - Usa `StorageClass` con replicación/snapshots.
   - Considera `StatefulSet` en lugar de Pod si necesitas actualizaciones sin perder datos.

---

## Referencias
- [Kubernetes volumeMode](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#volume-mode)
- [OpenShift SecurityContextConstraints](https://docs.openshift.com/container-platform/latest/authentication/managing-security-context-constraints.html)
- [PostgreSQL initialization](https://hub.docker.com/_/postgres)
