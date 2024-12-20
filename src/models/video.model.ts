import { Table, Column, Model, DataType, PrimaryKey, Default, AllowNull, ForeignKey } from 'sequelize-typescript';
import { v4 as uuidv4 } from 'uuid';

@Table({
  tableName: 'videos',
  timestamps: true
})
export class Video extends Model {
  @PrimaryKey
  @Default(uuidv4)
  @Column(DataType.UUID)
  id!: string;

  @AllowNull(false)
  @Column(DataType.UUID)
  userId!: string;

  @AllowNull(false)
  @Column(DataType.STRING)
  filename!: string;

  @AllowNull(false)
  @Default('processing')
  @Column(DataType.ENUM('processing', 'completed', 'failed'))
  status!: 'processing' | 'completed' | 'failed';

  @AllowNull(true)
  @Column(DataType.TEXT)
  prdDocument!: string;

  @AllowNull(true)
  @Column(DataType.TEXT)
  businessPlan!: string;
}

export default Video;
