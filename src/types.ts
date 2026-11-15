export interface MO2Executable {
  title: string;
  binary: string;
  arguments: string;
}

export interface MO2Instance {
  id: string;
  displayName: string;
  instanceType: "portable" | "global";
  instanceName: string;
  gameName: string;
  gamePathLinux: string;
  mo2ExeLinux: string;
  mo2IniLinux: string;
  selectedProfile: string;
  executables: MO2Executable[];
  defaultExecutable: string;
  launcherSource: "steam" | "heroic" | "lutris" | "custom";
  prefixPath: string;
  protonBinaryPath: string;
  envOverrides: Record<string, string>;
  isValid: boolean;
  validationError?: string;
}

export interface PrefixOption {
  id: string;
  label: string;
  launcherSource: string;
  installPath: string;
}

export interface ProtonOption {
  id: string;
  label: string;
}