import { Table, Column, Model, DataType, PrimaryKey, Default, AllowNull, ForeignKey } from 'sequelize-typescript';
import { v4 as uuidv4 } from 'uuid';
import { Video } from './video.model';

@Table({
  tableName: 'analyses',
  timestamps: true
})
export class Analysis extends Model {
  @PrimaryKey
  @Default(uuidv4)
  @Column(DataType.UUID)
  id!: string;

  @ForeignKey(() => Video)
  @AllowNull(false)
  @Column(DataType.UUID)
  videoId!: string;

  @AllowNull(false)
  @Default([])
  @Column(DataType.ARRAY(DataType.STRING))
  frames!: string[];

  @AllowNull(false)
  @Default([])
  @Column(DataType.ARRAY(DataType.TEXT))
  ocrText!: string[];

  @AllowNull(false)
  @Default([])
  @Column(DataType.ARRAY(DataType.TEXT))
  features!: string[];

  @AllowNull(false)
  @Default([])
  @Column(DataType.ARRAY(DataType.TEXT))
  userFlow!: string[];
}

export default Analysis;
