import Lake
open Lake DSL

package «standard-model» where
  -- add package configuration options here

lean_lib «StandardModel» where
  -- add library configuration options here

@[default_target]
lean_exe «standard-model» where
  root := `Main
