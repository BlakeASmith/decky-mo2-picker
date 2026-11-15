import { callable } from "@decky/api";
import {
  DialogBody,
  DialogButton,
  DialogButtonPrimary,
  DialogFooter,
  DialogHeader,
  Dropdown,
  DropdownOption,
  Field,
  ModalRoot,
  TextField,
  ToggleField,
} from "@decky/ui";
import { useEffect, useState } from "react";
import { MO2Instance, PrefixOption, ProtonOption } from "../types";

const getPrefixes = callable<[], PrefixOption[]>("get_available_prefixes");
const getProtons = callable<[], ProtonOption[]>("get_available_protons");
const saveOverride = callable<
  [instanceId: string, overrideData: Record<string, unknown>],
  void
>("save_instance_override");

interface Props {
  instance: MO2Instance;
  closeModal?: () => void;
  onSaved: () => void;
}

export function InstanceConfigModal({ instance, closeModal, onSaved }: Props) {
  const [displayName, setDisplayName] = useState(instance.displayName);
  const [prefixPath, setPrefixPath] = useState(instance.prefixPath);
  const [protonPath, setProtonPath] = useState(instance.protonBinaryPath);
  const [defaultExecutable, setDefaultExecutable] = useState(
    instance.defaultExecutable,
  );
  const [dllOverrides, setDllOverrides] = useState(
    instance.envOverrides.WINEDLLOVERRIDES ?? "",
  );
  const [prefixes, setPrefixes] = useState<PrefixOption[]>([]);
  const [protons, setProtons] = useState<ProtonOption[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void Promise.all([getPrefixes(), getProtons()]).then(([p, pr]) => {
      setPrefixes(p);
      setProtons(pr);
    });
  }, []);

  const prefixOptions: DropdownOption[] = prefixes.map((p) => ({
    data: p.id,
    label: p.label,
  }));
  const protonOptions: DropdownOption[] = protons.map((p) => ({
    data: p.id,
    label: p.label,
  }));
  const exeOptions: DropdownOption[] = instance.executables.map((e) => ({
    data: e.title,
    label: e.title,
  }));

  const save = async () => {
    setBusy(true);
    await saveOverride(instance.id, {
      displayName,
      prefixPath,
      protonBinaryPath: protonPath,
      defaultExecutable,
      envOverrides: { WINEDLLOVERRIDES: dllOverrides },
    });
    setBusy(false);
    onSaved();
    closeModal?.();
  };

  return (
  <ModalRoot closeModal={closeModal}>
    <DialogHeader>Configure {instance.gameName}</DialogHeader>
    <DialogBody>
      <Field label="Display name">
        <TextField value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
      </Field>
      <Field label="Target prefix">
        <Dropdown
          rgOptions={prefixOptions}
          selectedOption={prefixPath}
          onChange={(opt) => setPrefixPath(String(opt.data))}
        />
      </Field>
      <Field label="Proton version">
        <Dropdown
          rgOptions={protonOptions}
          selectedOption={protonPath}
          onChange={(opt) => setProtonPath(String(opt.data))}
        />
      </Field>
      <Field label="Default executable">
        <Dropdown
          rgOptions={exeOptions}
          selectedOption={defaultExecutable}
          onChange={(opt) => setDefaultExecutable(String(opt.data))}
        />
      </Field>
      <Field label="WINEDLLOVERRIDES">
        <TextField value={dllOverrides} onChange={(e) => setDllOverrides(e.target.value)} />
      </Field>
      <Field label="Instance type">
        <ToggleField
          label={`${instance.instanceType} / ${instance.launcherSource}`}
          checked={instance.isValid}
          disabled
        />
      </Field>
    </DialogBody>
    <DialogFooter>
      <DialogButton onClick={closeModal}>Cancel</DialogButton>
      <DialogButtonPrimary onClick={save} disabled={busy}>
        Save
      </DialogButtonPrimary>
    </DialogFooter>
  </ModalRoot>
  );
}