

-- -----------------------------------------------------
-- Table `aurora`.`estados`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `aurora`.`estados` (
  `ID_Estados` INT(11) NOT NULL AUTO_INCREMENT,
  `Nombre_estado` VARCHAR(45) NULL DEFAULT NULL,
  `Fecha_Creacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  PRIMARY KEY (`ID_Estados`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

-- -----------------------------------------------------
-- Table `aurora`.`area`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `aurora`.`area` (
  `ID_Area` INT(11) NOT NULL AUTO_INCREMENT,
  `Nombre_Area` VARCHAR(45) NULL DEFAULT NULL,
  `Descripcion_Area` VARCHAR(45) NULL,
  `estados_ID_Estados` INT(11) NOT NULL,
  `Fecha_Creada` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `Fecha_Actualizacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  PRIMARY KEY (`ID_Area`),
  INDEX `fk_area_estados1_idx` (`estados_ID_Estados` ASC),
  UNIQUE INDEX `ID_Area_UNIQUE` (`ID_Area` ASC),
  CONSTRAINT `fk_area_estados1`
    FOREIGN KEY (`estados_ID_Estados`)
    REFERENCES `aurora`.`estados` (`ID_Estados`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;

-- -----------------------------------------------------
-- Table `aurora`.`cargo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `aurora`.`cargo` (
  `ID_Cargo` INT(11) NOT NULL AUTO_INCREMENT,
  `cargo` VARCHAR(45) NULL DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  PRIMARY KEY (`ID_Cargo`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;

-- -----------------------------------------------------
-- Table `aurora`.`empleados`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `aurora`.`empleados` (
  `ID_Empleado` INT(11) NOT NULL AUTO_INCREMENT,
  `Nombres` VARCHAR(45) NULL DEFAULT NULL,
  `Apellidos` VARCHAR(45) NULL DEFAULT NULL,
  `Correo_Electronico` VARCHAR(45) NULL DEFAULT NULL,
  `Contrasena` VARCHAR(500) NULL DEFAULT NULL,  -- Corregido el tamaño de VARCHAR
  `Celular` VARCHAR(45) NULL DEFAULT NULL,
  `Login` VARCHAR(45) NULL,
  `Cargo_id` INT(11) NOT NULL,
  `estados_ID_Estados` INT(11) NOT NULL,
  `Fecha_Creacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `Fecha_Actualizacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `area_ID_Area` INT(11) NOT NULL,
  PRIMARY KEY (`ID_Empleado`, `area_ID_Area`),
  UNIQUE INDEX `Correo_Electronico_UNIQUE` (`Correo_Electronico` ASC),
  INDEX `fk_Empleados_Cargo_idx` (`Cargo_id` ASC),
  UNIQUE INDEX `Login_UNIQUE` (`Login` ASC),
  UNIQUE INDEX `Celular_UNIQUE` (`Celular` ASC),
  INDEX `fk_empleados_estados1_idx` (`estados_ID_Estados` ASC),
  INDEX `fk_empleados_area1_idx` (`area_ID_Area` ASC),
  CONSTRAINT `fk_Empleados_Cargo`
    FOREIGN KEY (`Cargo_id`)
    REFERENCES `aurora`.`cargo` (`ID_Cargo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_empleados_estados1`
    FOREIGN KEY (`estados_ID_Estados`)
    REFERENCES `aurora`.`estados` (`ID_Estados`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_empleados_area1`
    FOREIGN KEY (`area_ID_Area`)
    REFERENCES `aurora`.`area` (`ID_Area`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8;

-- -----------------------------------------------------
-- Table `aurora`.`prioridad`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `aurora`.`prioridad` (
  `ID_Prioridad` INT(11) NOT NULL AUTO_INCREMENT,
  `Nombre_prioridad` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`ID_Prioridad`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

-- -----------------------------------------------------
-- Table `aurora`.`proyecto`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `aurora`.`proyecto` (
  `ID_Proyecto` INT(11) NOT NULL AUTO_INCREMENT,
  `Nombre` VARCHAR(45) NULL DEFAULT NULL,
  `Descripcion` VARCHAR(45) NULL DEFAULT NULL,
  `Duracion_estimada` INT(11) NULL DEFAULT NULL,
  `Estados_ID_Estados` INT(11) NOT NULL,
  `Prioridad_ID_Prioridad` INT(11) NOT NULL,
  `Fecha_Creacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `Fecha_Fin_Proyecto` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  PRIMARY KEY (`ID_Proyecto`),
  INDEX `fk_Proyecto_Estados1_idx` (`Estados_ID_Estados` ASC),
  INDEX `fk_Proyecto_Prioridad1_idx` (`Prioridad_ID_Prioridad` ASC),
  CONSTRAINT `fk_Proyecto_Estados1`
    FOREIGN KEY (`Estados_ID_Estados`)
    REFERENCES `aurora`.`estados` (`ID_Estados`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Proyecto_Prioridad1`
    FOREIGN KEY (`Prioridad_ID_Prioridad`)
    REFERENCES `aurora`.`prioridad` (`ID_Prioridad`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

-- -----------------------------------------------------
-- Table `aurora`.`empleados_proyecto`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `aurora`.`empleados_proyecto` (
  `ID_emple_vs_proye` VARCHAR(45) NOT NULL,
  `Empleados_ID_Empleado` INT(11) NOT NULL,
  `Proyecto_ID_Proyecto` INT(11) NOT NULL,
  `Fecha_asignacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `fecha_actualizacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  PRIMARY KEY (`ID_emple_vs_proye`, `Empleados_ID_Empleado`, `Proyecto_ID_Proyecto`),
  INDEX `fk_Empleados_has_Proyecto_Proyecto1_idx` (`Proyecto_ID_Proyecto` ASC),
  INDEX `fk_Empleados_has_Proyecto_Empleados1_idx` (`Empleados_ID_Empleado` ASC),
  CONSTRAINT `fk_Empleados_has_Proyecto_Empleados1`
    FOREIGN KEY (`Empleados_ID_Empleado`)
    REFERENCES `aurora`.`empleados` (`ID_Empleado`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Empleados_has_Proyecto_Proyecto1`
    FOREIGN KEY (`Proyecto_ID_Proyecto`)
    REFERENCES `aurora`.`proyecto` (`ID_Proyecto`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

-- -----------------------------------------------------
-- Table `aurora`.`tareas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `aurora`.`tareas` (
  `ID_Tareas` INT(11) NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(45) NULL DEFAULT NULL,
  `Descripcion` VARCHAR(450) NULL DEFAULT NULL,
  `Duracion_estimada` INT(11) NULL DEFAULT NULL,
  `Prioridad_ID_Prioridad` INT(11) NOT NULL,
  `proyecto_ID_Proyecto` INT(11) NOT NULL,
  `Fecha_Creacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `Fecha_Fin` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  PRIMARY KEY (`ID_Tareas`),
  INDEX `fk_Tareas_Prioridad1_idx` (`Prioridad_ID_Prioridad` ASC),
  INDEX `fk_tareas_proyecto1_idx` (`proyecto_ID_Proyecto` ASC),
  CONSTRAINT `fk_Tareas_Prioridad1`
    FOREIGN KEY (`Prioridad_ID_Prioridad`)
    REFERENCES `aurora`.`prioridad` (`ID_Prioridad`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tareas_proyecto1`
    FOREIGN KEY (`proyecto_ID_Proyecto`)
    REFERENCES `aurora`.`proyecto` (`ID_Proyecto`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

-- -----------------------------------------------------
-- Table `aurora`.`subtareas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `aurora`.`subtareas` (
  `ID_Subtarea` INT(11) NOT NULL AUTO_INCREMENT,
  `Nombre_Subtarea` VARCHAR(45) NULL DEFAULT NULL,
  `Descripcion` VARCHAR(450) NULL DEFAULT NULL,  
  `Duracion_estimada` INT(11) NULL DEFAULT NULL,
  `Tareas_ID_Tareas` INT(11) NOT NULL,
  `Fecha_Creacion` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `Fecha_Fin` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  PRIMARY KEY (`ID_Subtarea`),
  INDEX `fk_Subtareas_Tareas1_idx` (`Tareas_ID_Tareas` ASC),
  CONSTRAINT `fk_Subtareas_Tareas1`
    FOREIGN KEY (`Tareas_ID_Tareas`)
    REFERENCES `aurora`.`tareas` (`ID_Tareas`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET SQL_MODE=@OLD_SQL_MODE;