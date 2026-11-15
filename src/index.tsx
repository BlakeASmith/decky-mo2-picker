import { callable, definePlugin } from "@decky/api";
import {
  ButtonItem,
  Dropdown,
  DropdownOption,
  PanelSection,
  PanelSectionRow,
  showModal,
  staticClasses,
} from "@decky/ui";
import { useCallback, useEffect, useState } from "react";
import { FaPuzzlePiece } from "react-icons/fa";
import { InstanceConfigModal } from "./components/InstanceConfigModal";
import { MO2Instance } from "./types";

const getInstances = callable<[forceRescan?: boolean], MO2Instance[]>(
  "get_instances",
);
const launchMo2 = callable<[instanceId: string], { success: boolean; error?: string }>(
  "launch_mo2",
);
const launchGame = callable<
  [instanceId: string, executableTitle?: string],
  { success: boolean; error?: string }
>("launch_game");

function badgeFor(instance: MO2Instance): string {
  if (instance.instanceType === "portable") return "Portable";
  return instance.launcherSource === "custom"
    ? "Global"
    : instance.launcherSource.toUpperCase();
}

function protonLabel(path: string): string {
  if (!path) return "Unknown";
  const parts = path.split("/");
  const idx = parts.findIndex((p) => p === "common" || p === "compatibilitytools.d");
  if (idx >= 0 && parts[idx + 1]) return parts[idx + 1];
  return parts[parts.length - 2] ?? path;
}

function InstanceSection({ instance, onRefresh }: { instance: MO2Instance; onRefresh: () => void }) {
  const [executable, setExecutable] = useState(instance.defaultExecutable);
  const exeOptions: DropdownOption[] = instance.executables.map((e) => ({
    data: e.title,
    label: e.title,
  }));

  return (
    <PanelSection title={`${instance.displayName} [${badgeFor(instance)}]`}>
      <PanelSectionRow>
        Profile: {instance.selectedProfile || "Default"} · Proton: {protonLabel(instance.protonBinaryPath)}
      </PanelSectionRow>
      {!instance.isValid && (
        <PanelSectionRow>
          ⚠ {instance.validationError ?? "Configuration required"}
        </PanelSectionRow>
      )}
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={async () => {
            const res = await launchGame(instance.id, executable);
            if (!res.success) console.error(res.error);
          }}
        >
          Launch Game ({executable || "none"})
        </ButtonItem>
      </PanelSectionRow>
      <PanelSectionRow>
        <ButtonItem layout="below" onClick={() => void launchMo2(instance.id)}>
          Open MO2
        </ButtonItem>
      </PanelSectionRow>
      {exeOptions.length > 0 && (
        <PanelSectionRow>
          <Dropdown
            rgOptions={exeOptions}
            selectedOption={executable}
            onChange={(opt) => setExecutable(String(opt.data))}
          />
        </PanelSectionRow>
      )}
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={() =>
            showModal(
              <InstanceConfigModal instance={instance} onSaved={onRefresh} />,
            )
          }
        >
          Configure Instance
        </ButtonItem>
      </PanelSectionRow>
    </PanelSection>
  );
}

function Content() {
  const [instances, setInstances] = useState<MO2Instance[]>([]);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async (force = false) => {
    setLoading(true);
    try {
      setInstances(await getInstances(force));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return (
    <>
      <PanelSection title="MO2 Universal Launcher">
        <PanelSectionRow>
          <ButtonItem layout="below" onClick={() => void refresh(true)} disabled={loading}>
            {loading ? "Scanning…" : "Rescan Instances"}
          </ButtonItem>
        </PanelSectionRow>
      </PanelSection>
      {instances.length === 0 && (
        <PanelSection title="No instances">
          <PanelSectionRow>Run a rescan after installing MO2.</PanelSectionRow>
        </PanelSection>
      )}
      {instances.map((inst) => (
        <InstanceSection key={inst.id} instance={inst} onRefresh={() => void refresh(true)} />
      ))}
    </>
  );
}

export default definePlugin(() => ({
  name: "MO2 Universal Launcher",
  titleView: <div className={staticClasses.Title}>MO2 Universal Launcher</div>,
  content: <Content />,
  icon: <FaPuzzlePiece />,
  onDismount() {},
}));